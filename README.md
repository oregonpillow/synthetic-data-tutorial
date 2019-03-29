# Anonymisation with Synthetic Data Tutorial

## Some questions

**What is this?**

A hands-on tutorial showing how to use Python to create synthetic data.

**Wait, what is this "synthetic data" you speak of?**

It's data that is created by an automated process which contains many of the statistical patterns of an original dataset. It is also sometimes used as a way to release data that has no personal information in it, even if the original did contain lots of data that could identify people. This means programmers and data scientists can crack on building software and algorithms that they know will work similarly on the real data.

**Who is this tutorial for?**

For any person who programs who wants to learn about data anonymisation in general or more specifically about synthetic data.

**What is it not for?**

Non-programmers. Although we think this tutorial is still worth a browse to get some of the main ideas in what goes in to anonymising a dataset. However, if you're looking for info on how to create synthetic data using the latest and greatest deep learning techniques, this is not the tutorial for you.

**Who are you?**

We're the Open Data Institute. We work with companies and governments to build an open, trustworthy data ecosystem. Anonymisation and synthetic data are some of the many, many ways we can responsbily increase access to data. If you want to learn more, [check out our site](http://theodi.org).

**Why did you make this?**

We have an [R&D programme](https://theodi.org/project/data-innovation-for-uk-research-and-development/) that has a number of projects looking in to how to support innovation, improve data infrastructure and encourage ethical data sharing. One of our projects is about [managing the risks of re-identification](https://theodi.org/project/rd-broaden-access-to-personal-data-while-protecting-privacy-and-creating-a-fair-market/) in shared and open data. As you can see in the *Key outputs* section, we have other material from the project, but we thought it'd be good to have something specifically aimed at programmmers who are interested in learning by doing.

**Speaking of which, can I just get to the tutorial now?**

Sure! Let's go.

## Overview

In this tutorial you are aiming to open accident and emergency (A&E) data from multiple hospitals in London. This data obviously contains some sensitive personal information about people's health and can't be openly shared. By removing and altering certain identifying information in the data we can greatly reduce the risk that patients can be re-identified.

The practical steps involve:

1. Create an A&E admissions dataset which will contain (pretend) personal information.
2. Run some anonymisation steps over this dataset to generate a new dataset with much less re-identification risk.
3. Take this de-identified dataset and generate multiple synthetic datasets from it to reduce the re-identification risk even further.
4. Analyse the synthetic datasets to see how similar they are to the original data.

You may be wondering, why can't we just do synthetic data step? If it's synthetic surely it won't contain any personal information?

Not exactly. Patterns picked up in the original data can be transferred to the synthetic data. This is especially true for outliers. For instance if there is only one person from an certain area over 85 and this shows up in the synthetic data, we would be able to re-identify them.

## Credit to others

This tutorial is inspired by the [NHS England and ODI Leeds' research](https://odileeds.org/events/synae/) in to creating a synthetic dataset from NHS England's accident and emergency admissions. Please do read about their project, as it's really interesting and great for learning about the benefits and risks in creating synthetic data. Just to be clear, we're not using their data but are creating our own simple, mock version of it. We, of course, don't have access to the NHS's highly sensitive A&E data (and nor should we!).

Also, the synthetic data generating library we use is [DataSynthetizer](https://homes.cs.washington.edu/~billhowe//projects/2017/07/20/Data-Synthesizer.html) and comes as part of this codebase. Coming out of University of Washington, it's an excellent piece of software and their research and papers are well worth checking out.  

---

## Setup

First, make sure you have [Python3 installed](https://www.python.org/downloads/). Minimum Python 3.5.

Download this repository either as a zip or using Git.

Change direcory in to the repo, install a virtualenv and install the dependent libaries.

```bash
cd /path/to/repo/synthetic_data_tutorial/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Next we'll go through how to create, de-identify and synthesis the code. We'll show this using code snippets but the full code is contained within the `/tutorial` directory.

There's small differences between the code presented here and what's in the Python scripts but it's mostly down to variable naming. I'd encourage you to run, edit and play with the code locally.

## Generate mock NHS A&E dataset

The data already exists in `data/nhs_ae_mock.csv` so feel free to browse that. But you should generate your own fresh dataset using the `tutorial/generate.py` script. To do this, you'll need to download one dataset first. It's a list of all postcodes in London. You can find it at this page on [doogal.co.uk](https://www.doogal.co.uk/PostcodeDownloads.php), at the _London_ link under the _By English region_ section. Or just download it directly at [this link](https://www.doogal.co.uk/UKPostcodesCSV.ashx?region=E12000007) (just take note, it's 133MB in size).

Then place the `London postcodes.csv` file in to the `synthetic-data-tutorial/data` directory.

```bash
mv "/path/to/dataset/London postcodes" /path/to/repo/synthetic-data-tutorial/data
```

Next simply go to the project root directory and run the `generate.py` script.

```bash
python tutorial/generate.py
```

Voila! You'll now see a `hospital_ae_data.csv` file in the `/data` directory. Open it up and have a browse. It's contains the following columns:

- **Attendance ID**: a unique ID generated for every admission to A&E
- **Health Service ID**: NHS number of the admitted patient  
- **Hospital**: which hospital admitted the patient
- **Arrival Time**: what time and date the patient was admitted
- **Time in A&E (mins)**: time (in minutes) of how long the patient spent in A&E
- **Treatment**: what the person was treated for
- **Gender**: patient gender, see [NHS patient gender codes](https://www.datadictionary.nhs.uk/data_dictionary/attributes/p/person/person_gender_code_de.asp?shownav=1)
- **Age**: age of patient
- **Postcode**: postcode of patient

We can see this dataset obviously contains some personal information. For instance, if we knew roughly the time a neighbour went to A&E we could use their postcode to figure out exactly what ailment they went in with. Or, if a list of people's Health Service ID's were to be leaked in future, lots of people could be re-identified.

Because of this, we'll need to take some de-identification steps.

---

## De-identification

For this stage we're going to be loosely following the de-identification techniques used when NHS England was [creating its own synthetic data](https://odileeds.org/blog/2019-01-24-exploring-methods-for-creating-synthetic-a-e-data).

We pass the data through the following de-identification process. If you look in `tutorial/deidentify.py` you'll see the steps involved in this.

It first loads the `data/nhs_ae_data.csv` file in to the Pandas DataFrame as `nhs_ae_df`.

```python
nhs_ae_df = pd.read_csv(filepaths.nhs_ae_data)
```

### Remove NHS numbers

NHS numbers are direct identifiers and should be removed. So we'll drop the entire column.

```python
nhs_ae_df = nhs_ae_df.drop('NHS number', 1)
```

### Where a patient lives

Pseudo-indentifiers, also known as [quasi-identifiers](https://en.wikipedia.org/wiki/Quasi-identifier), are pieces of information that don't directly identify people but can used with other information to identify a person. If someone were to take the age, postcode and gender of a person they could combine these and check the dataset to see what that person went to A&E with.

> I started with the postcode of the patients resident lower super output area (LSOA). This is a geographical definition with an average of 1500 residents created to make reporting in England and Wales easier. I wanted to keep some basic information about the area where the patient lives whilst completely removing any information regarding any actual postcode. A key variable in health care inequalities is the patients Index of Multiple deprivation (IMD) decile (broad measure of relative deprivation) which gives an average ranked value for each LSOA. By replacing the patients resident postcode with an IMD decile I have kept a key bit of information whilst making this field non-identifiable.

We'll do just the same with our dataset.

First we'll map the postcodes to their LSOA and drop the postcodes.

```python
postcodes_df = pd.read_csv(filepaths.postcodes_london)
nhs_ae_df = pd.merge(
    nhs_ae_df,
    postcodes_df[['Postcode', 'Lower layer super output area']],
    on='Postcode'
)
nhs_ae_df = nhs_ae_df.drop('Postcode', 1)
```

Then we'll add a mapped coliumn  of "Index of Multiple Deprivation" column for each entry's LSOA.

```python
nhs_ae_df = pd.merge(
    nhs_ae_df,
    postcodes_df[
        ['Lower layer super output area', 'Index of Multiple Deprivation']
    ].drop_duplicates(),
    on='Lower layer super output area'
)
```

Then we'll calculate the decile bins for the IMD by taking all the IMD for our list of London. We'll use the pandas `qcut` (quantile cut), function for this. 

```python
_, bins = pd.qcut(
    postcodes_df['Index of Multiple Deprivation'], 10,
    retbins=True, labels=False)
```

Then we'll use those decile `bins` to map each row's IMD to its IMD decile.

```python
nhs_ae_df['Index of Multiple Deprivation Decile'] = pd.cut(
    nhs_ae_df['Index of Multiple Deprivation'],
    bins=bins,
    labels=False, include_lowest=True) + 1
```

And finally drop the columns we no longer need.

```python
nhs_ae_df = nhs_ae_df.drop('Index of Multiple Deprivation', 1)
nhs_ae_df = nhs_ae_df.drop('Lower layer super output area', 1)
```

### Individual hospitals

When talking about this section NHS England described it as:

> As each hospital has its own complex case mix and health system, using these data to identify poor performance or possible improvements would be invalid and un-helpful. Therefore, I decided to replace the hospital code with a random number.

So let's do just that.

```python
    hospitals = list(set(nhs_ae_df['Hospital'].tolist()))
    random.shuffle(hospitals)
    hospital_ids = range(1, len(hospitals)+1)
    hospitals_map = {
        hospital : hospital_id
        for hospital, hospital_id in zip(hospitals, hospital_ids)
    }
    nhs_ae_df['Hospital ID'] = nhs_ae_df['Hospital'].map(hospitals_map)
    nhs_ae_df = nhs_ae_df.drop('Hospital', 1)
```

### Time in the data

> The next obvious step was to simplify some of the time information I have available as health care system analysis doesn't need to be responsive enough to work on a second and minute basis. Thus, I removed the time information from the 'arrival date', mapped the 'arrival time' into 4-hour chunks

```python
arrival_times = pd.to_datetime(nhs_ae_df['Arrival Time'])
nhs_ae_df['Arrival Date'] = arrival_times.dt.strftime('%Y-%m-%d')
nhs_ae_df['Arrival Hour'] = arrival_times.dt.hour

nhs_ae_df['Arrival hour range'] = pd.cut(
    nhs_ae_df['Arrival Hour'], 
    bins=[0, 4, 8, 12, 16, 20, 24], 
    labels=['00-03', '04-07', '08-11', '12-15', '16-19', '20-23'], 
    include_lowest=True
)
nhs_ae_df = nhs_ae_df.drop('Arrival Time', 1)
nhs_ae_df = nhs_ae_df.drop('Arrival Hour', 1)
```

### Patient demographics

> I decided to only include records with a sex of male or female in order to reduce risk of re identification through low numbers. 

```python
hospital_ae_df = hospital_ae_df[hospital_ae_df['Gender'].isin(['Male', 'Female'])]
```

> For the patients age it is common practice to group these into bands and so I've used a standard set - 1-17, 18-24, 25-44, 45-64, 65-84, and 85+ - which although are non-uniform are well used segments defining different average health care usage.

```python
hospital_ae_df['Age bracket'] = pd.cut(
    hospital_ae_df['Age'],
    bins=[0, 18, 25, 45, 65, 85, 150],
    labels=['0-17', '18-24', '25-44', '45-64', '65-84', '85-'],
    include_lowest=True
)
hospital_ae_df = hospital_ae_df.drop('Age', 1)
```

### Health care coding

---

## Synthesising

Now we've gotten to the stage where we'll create a synthetic version of our de-identified data.

Synthetic data exists on a spectrum from merely the same structure as the original data to carrying most of the statistical patterns of the original dataset. The columns all contain data similar in type to the original but vary in how similar they are to the origianl. 

We'll make three types of synthetic data.

1. Random – the values are generated randomly and bare no relation to the statistical patterns in the original data.
2. Independent – The values are similar to the original data but contain no correlation info.  
3. Correlated – Correlation info is kept in

### DataSynthesizer

> DataSynthesizer consists of three high-level modules:
>
> 1. DataDescriber: investigates the data types, correlations and distributions of the attributes in the private dataset, and produces a data summary.
> 2. DataGenerator: samples from the summary computed by DataDescriber and outputs synthetic data
> 3. ModelInspector: shows an intuitive description of the data summary that was computed by DataDescriber, allowing the data owner to evaluate the accuracy of.

For each of three we'll run our tests we defined and observe the results. These are three modes available in Data Synthesizer toolkit.

### Random mode - generate random values for this column

If we were just to generate data for testing our software. We wouldn't care too much about the statistical patterns within the data. Just that it was roughly a similar size and that the datatypes and columns aligned.

In this case, we can just generate the data at random using the `generate_dataset_in_random_mode` function within the `DataGenerator` class.

#### Data Description: Random

The first step is to create a description of the data, defining the datatypes and which are the categorical variables.

```python
attribute_to_datatype = {
    'Attendance ID': 'String',
    'Time in A&E (mins)': 'Integer',
    'Treatment': 'String',
    'Gender': 'String',
    'Index of Multiple Deprivation Decile': 'Integer',
    'Hospital ID': 'String',
    'Arrival Date': 'String',
    'Arrival hour range': 'String',  
    'Age bracket': 'String'
}

attribute_is_categorical = {
    'Attendance ID': False,
    'Hospital ID': True,
    'Time in A&E (mins)': False,
    'Treatment': True,
    'Gender': True,
    'Index of Multiple Deprivation Decile': False,
    'Arrival Date': True,
    'Arrival hour range': True,  
    'Age bracket': True
}
```

Then create a description file, specificying where the data is and its attritube types.

```python
describer.describe_dataset_in_random_mode(
    filepaths.hospital_ae_data_deidentify,
    attribute_to_datatype=attribute_to_datatype,
    attribute_to_is_categorical=attribute_is_categorical)
```

You can see an example description file in `data/hospital_ae_description_random.json`.

#### Data Generation: Random

Next generate the random data. We'll just generate the same amount of rows as was in the original data but, importantly, we could generate much more or less if we wanted to.

```python
num_rows = len(hospital_ae_df)
```

Now generate the random data

```python
generator = DataGenerator()
generator.generate_dataset_in_random_mode(
    num_rows, filepaths.hospital_ae_description_random)
generator.save_synthetic_data(filepaths.hospital_ae_data_synthetic_random)
```

#### Attribute Comparison: Random

We'll compare each attribute in the original data to the synthetic data by generating plots of histograms using the `ModelInspector` class.

```python
synthetic_df = pd.read_csv(synthetic_data_filepath)

# Read attribute description from the dataset description file.
attribute_description = read_json_file(description_filepath)['attribute_description']

inspector = ModelInspector(hospital_ae_df, synthetic_df, attribute_description)

for attribute in synthetic_df.columns:
    inspector.compare_histograms(attribute, figure_filepath)
```

Let's look at the histogram plots now for a few of the attributes. We can that the data generated is completely random and doesn't contain any information about averages or distributions.

*Comparison of ages in original data (left) and random synthetic data (right)*
![Random mode age bracket histograms](plots/random_Age_bracket.png)

*Comparison of hospital attendance in original data (left) and random synthetic data (right)*
![Random mode age bracket histograms](plots/random_Hospital_ID.png)

*Comparison of arrival date in original data (left) and random synthetic data (right)*
![Random mode age bracket histograms](plots/random_Arrival_Date.png)

You can see more examples in the `/plots` directory.

#### Compare pairwise mutual information: Random

**WORK IN PROGRESS**

No correlations.

*Mutual Information Heatmap in original data (left) and random synthetic data (right)*
![Random mode age mutual information](plots/mutual_information_heatmap_random.png)

### Independent attribute mode - keep the patterns of each individual column

What if we had the use case where we wanted to build models to analyse the medians of ages, or hospital usage? In this case we'd use independent attribute mode.

We'll describe and generate the independent data now.

#### Data Description: Independent

```python
describer.describe_dataset_in_independent_attribute_mode(
    filepaths.hospital_ae_data_deidentify,
    attribute_to_datatype=attribute_to_datatype,
    attribute_to_is_categorical=attribute_is_categorical)

describer.save_dataset_description_to_file(description_filepath)
```

#### Data Generation: Independent

Next generate the data which keep the distributions of each column but not the data correlations.

```python
generator = DataGenerator()
generator.generate_dataset_in_independent_mode(num_rows, description_filepath)
generator.save_synthetic_data(synthetic_data_filepath)
```

#### Attribute Comparison: Independent

Comparing the attibute histograms we see the independent mode captures the distributions pretty accurately. You can see the synthetic data is _mostly_ similar but not exactly.

```python
synthetic_df = pd.read_csv(synthetic_data_filepath)
attribute_description = read_json_file(description_filepath)['attribute_description']
inspector = ModelInspector(hospital_ae_df, synthetic_df, attribute_description)
for attribute in synthetic_df.columns:
    inspector.compare_histograms(attribute, figure_filepath)
```

*Comparison of ages in original data (left) and independent synthetic data (right)*
![Random mode age bracket histograms](plots/independent_Age_bracket.png)

*Comparison of hospital attendance in original data (left) and independent synthetic data (right)*
![Random mode age bracket histograms](plots/independent_Hospital_ID.png)

*Comparison of arrival date in original data (left) and independent synthetic data (right)*
![Random mode age bracket histograms](plots/independent_Arrival_Date.png)

#### Compare pairwise mutual information: Independent

**WORK IN PROGRESS**

No correlations.

*Mutual Information Heatmap in original data (left) and independent synthetic data (right)*
![Independent mode mutual information](plots/mutual_information_heatmap_indepdendent.png)

### Correlated attribute mode - include correlations between columns in the data

Lastly, if we care about, say, the number of old people attending a certain hospital and the waiting times dependent on hospitals. We'll need correlated data. To do this we use correlated mode.

To understand how it works we need to understand Bayesian networks. These are graphs that show the dependency between different variables. You can read a very good tutorial on them at the [Probabilistic World site](https://www.probabilisticworld.com/bayesian-belief-networks-part-1/).

#### Data Description: Correlated

```python
describer.describe_dataset_in_correlated_attribute_mode(
    dataset_file=filepaths.hospital_ae_data_deidentify,
    epsilon=epsilon,
    k=degree_of_bayesian_network,
    attribute_to_datatype=attribute_to_datatype,
    attribute_to_is_categorical=attribute_is_categorical,
    attribute_to_is_candidate_key=attribute_to_is_candidate_key)

describer.save_dataset_description_to_file(description_filepath)
```

#### Data Generation: Correlated

```python
generator.generate_dataset_in_correlated_attribute_mode(
    num_rows, description_filepath)
generator.save_synthetic_data(synthetic_data_filepath)
```

#### Attribute Comparison: Correlated

We can see correlated mode keeps similar distributions also. It looks the exact same but if you look closely there are small differences in the distributions.

*Comparison of ages in original data (left) and correlated synthetic data (right)*
![Random mode age bracket histograms](plots/correlated_Age_bracket.png)

*Comparison of hospital attendance in original data (left) and independent synthetic data (right)*
![Random mode age bracket histograms](plots/correlated_Hospital_ID.png)

*Comparison of arrival date in original data (left) and independent synthetic data (right)*
![Random mode age bracket histograms](plots/correlated_Arrival_Date.png)

#### Compare pairwise mutual information: Correlated

**WORK IN PROGRESS**

Correlations.

*Mutual Information Heatmap in original data (left) and correlated synthetic data (right)*
![Independent mode mutual information](plots/mutual_information_heatmap_correlated.png)

---

### Wrap-up

That's about it really. There is much, much more to the world of anonymisation and synthetic data. Please check out more in the references below.

If you have any queries, comments or improvements about this tutorial please do get in touch. You can send me a message through Github or leave an Issue.

### References

- [A comparative study of synthetic dataset generation techniques](https://dl.comp.nus.edu.sg/bitstream/handle/1900.100/7050/TRA6-18.pdf?sequence=1&isAllowed=y) - Ashish Dandekar, Remmy A. M. Zen, Stéphane Bressan
- [Exploring methods for synthetic A&E data](https://odileeds.org/blog/2019-01-24-exploring-methods-for-creating-synthetic-a-e-data) - Jonathan Pearson, NHS with Open Data Institute Leeds.
- [DataSynthesizer Github Repository](https://github.com/DataResponsibly/DataSynthesizer)
- [DataSynthesizer: Privacy-Preserving Synthetic Datasets](https://faculty.washington.edu/billhowe/publications/pdfs/ping17datasynthesizer.pdf) Haoyue Ping, Julia Stoyanovich, Bill Howe. 2017.
