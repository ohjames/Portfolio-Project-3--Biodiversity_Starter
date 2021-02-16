import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import string
from itertools import chain
import numpy as np

#create DataFrames
observations = pd.read_csv('observations.csv')
species = pd.read_csv('species_info.csv')

# print(observations.head())

#fill in nan values for conservation_status
species.conservation_status.fillna('No Intervention', inplace = True)
# print(species.head())

#What is the distribution of conservation_status for animals?   #todo make graph look neater/find a way to present data better
conservation_dist = species[species.conservation_status != 'No Intervention'].groupby(['conservation_status', 'category']).scientific_name.count().unstack()
ax = conservation_dist.plot(kind = 'bar', figsize=(8,6), stacked = True)
ax.set_xlabel('Conservation Status')
ax.set_ylabel('Number of Species')
plt.show()

#Are certain types of species more likely to be endangered?     #todo present this information better
species['protection'] = species.conservation_status != 'No Intervention'
category_counts = species.groupby(['category', 'protection']).scientific_name.nunique().reset_index().pivot(columns = 'protection', index = 'category', values = 'scientific_name').reset_index()
category_counts.columns = ['category', 'unprotected', 'protected']
category_counts['percent_protected'] = category_counts.protected / (category_counts.protected + category_counts.unprotected) * 100
# print(category_counts)

#Are the differences between species and their conservation status significant?     #todo include more tests to this
table1 = [[30, 146], [75, 413]]
chi2, pval_mammal_bird, dof, expected = chi2_contingency(table1)
# print(pval_mammal_bird)   ~0.69
table2 = [[30, 146], [5, 73]]
chi2, pval_mammmal_reptile, dof, expected = chi2_contingency(table2)
# print(pval_mammmal_reptile)     ~0.04; significant

#Which animal is most prevalent and what is their distribution amongst parks?
def remove_punctuations(text):
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text
common_name = species[species.category == 'Mammal'].common_names.apply(remove_punctuations).str.split().tolist()
# common_name[:6]
cleandup = []
for item in common_name:
    item = list(dict.fromkeys(item))
    cleandup.append(item)
names = list(chain.from_iterable(i if isinstance(i, list) else [i] for i in cleandup))
word_count = []
for i in names:
    x = names.count(i)
    word_count.append((i, x))
# print(pd.DataFrame(set(word_count), columns=['Word', 'Count']).sort_values('Count', ascending= False).head(10))     #bat has the most
species['is_bat'] = species.common_names.str.contains(r"\bBat\b", regex = True)
# print(species.head(10))
bat_observations = observations.merge(species[species.is_bat])
# print(bat_observations)
bat_observations.groupby('park_name').observations.sum().reset_index()
obs_by_park = bat_observations.groupby(['park_name', 'protection']).observations.sum().reset_index()
# print(obs_by_park)
plt.figure(figsize=(14,6))
sns.barplot(x = obs_by_park.park_name, y = obs_by_park.observations, hue = obs_by_park.protection)
plt.xlabel('National Parks')
plt.ylabel('Number of Observations')
plt.title('Observations of Bats per Week')
plt.show()