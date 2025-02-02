from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from etherscan.accounts import Account
from etherscan.etherscan import Client
import json, requests
import argparse
import sys
import csv
import datetime, dateutil.parser
import string

with open('api_key.json', mode='r') as key_file:
    key = json.loads(key_file.read())['key']

ponzi = []
ponzi_file = "PonziData.csv"
non_ponzi = []
non_ponzi_file = "NonPonzi.csv"
features = pd.DataFrame(columns=['Address', 'Bal', 'N_maxpay', 'N_investment', 'N_payment', 'Paid_rate', 'Ponzi'])

with open(ponzi_file, encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=',', quotechar='|')
    for row in reader:
        addr_ponzi = ''.join(e for e in row[0] if e.isalnum())
        ponzi.append(addr_ponzi)

with open(non_ponzi_file, encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=',', quotechar='|')
    for row in reader:
        addr_non_ponzi = ''.join(e for e in row[0] if e.isalnum())
        non_ponzi.append(addr_non_ponzi)


def Paid_rate_division(n, d):
    return n / d if d else 0


for addr_ponzi in ponzi:
    addr_ponzi = ''.join(e for e in addr_ponzi if e.isalnum()).lower()
    print("Retrieving transactions and balance of contract ", addr_ponzi, "...", end=" \n")
    sys.stdout.flush()
    api = Client(api_key=key, cache_expire_after=5)
    text = api.get_transactions_by_address(addr_ponzi, tx_type='normal')
    tint = api.get_transactions_by_address(addr_ponzi, tx_type='internal')
    Bal = api.get_eth_balance(addr_ponzi)

    count_text = 0
    users_tint = 0
    N_investment = 0
    N_maxpay = 0
    N_payment = 0
    Paid_rate = 0
    ponzi_flag = 1

    for t in text:
        if (t['is_error'] is False):
            if t['to']:
                N_investment += 1
                if (t['value'] >= N_maxpay): N_maxpay = t['value']

    for t2 in tint:
        if (t2['is_error'] is False):
            if (t2['from'] == addr_ponzi):
                N_payment += 1
            elif (t2['to'] == addr_ponzi):
                N_investment += 1
                if (t2['value'] >= N_maxpay): N_maxpay = t2['value']

    Paid_rate = Paid_rate_division(N_payment, N_investment)

    print(addr_ponzi, round(Bal * 10 ** -18, 4), round(N_maxpay * 10 ** -18, 4), N_investment, N_payment,
          round(Paid_rate, 2), ponzi_flag)
    #    if (Bal > 0.0 and N_payment > 0.0 and N_investment > 0.0):
    features = features.append({'Address': addr_ponzi, 'Bal': Bal * 10 ** -18, 'N_maxpay': N_maxpay * 10 ** -18,
                                    'N_investment': N_investment, 'N_payment': N_payment, 'Paid_rate': Paid_rate,
                                    'Ponzi': ponzi_flag}, ignore_index=True)

for addr_non_ponzi in non_ponzi:
    addr_non_ponzi = ''.join(e for e in addr_non_ponzi if e.isalnum()).lower()
    print("Retrieving transactions and balance of contract ", addr_non_ponzi, "...", end=" \n")
    sys.stdout.flush()
    api = Client(api_key=key, cache_expire_after=5)
    text = api.get_transactions_by_address(addr_non_ponzi, tx_type='normal')
    tint = api.get_transactions_by_address(addr_non_ponzi, tx_type='internal')
    Bal = api.get_eth_balance(addr_non_ponzi)

    count_text = 0
    users_tint = 0
    N_investment = 0
    N_maxpay = 0
    N_payment = 0
    Paid_rate = 0
    ponzi_flag = 0

    for t in text:
        if (t['is_error'] is False):
            if t['to']:
                N_investment += 1
                if (t['value'] >= N_maxpay): N_maxpay = t['value']

    for t2 in tint:
        if (t2['is_error'] is False):
            if (t2['from'] == addr_non_ponzi):
                N_payment += 1
            elif (t2['to'] == addr_non_ponzi):
                N_investment += 1
                if (t2['value'] >= N_maxpay): N_maxpay = t2['value']

    Paid_rate = Paid_rate_division(N_payment, N_investment)
    print(addr_non_ponzi, round(Bal * 10 ** -18, 4), round(N_maxpay * 10 ** -18, 4), N_investment, N_payment,
          round(Paid_rate, 2), ponzi_flag)
    #    if (Bal > 0.0 and N_payment > 0.0 and N_investment > 0.0):
    features = features.append({'Address': addr_non_ponzi, 'Bal': Bal * 10 ** -18, 'N_maxpay': N_maxpay * 10 ** -18,
                                    'N_investment': N_investment, 'N_payment': N_payment, 'Paid_rate': Paid_rate,
                                    'Ponzi': ponzi_flag}, ignore_index=True)

'''
w,h = 150, 7
Matrix = [[0 for x in range(w)] for y in range(h)]
numpy [0][0] = 'Address'
Matrix [0][1] = 'Bal'
Matrix [0][2] = 'N_maxpay'
Matrix [0][3] = 'N_investment'
Matrix [0][4] = 'N_payment'
Matrix [0][5] = 'Paid_rate'
Matrix [0][6] = 'Ponzi'
print(Matrix)
'''

print(features)
# Labels are the values we want to predict
labels = np.array(features['Ponzi'])
# Remove the labels from the features
# axis 1 refers to the columns
features = features.drop('Ponzi', axis=1)
features = features.drop('Address', axis=1)
# Saving feature names for later use
feature_list = list(features.columns)
# Convert to numpy array
features = np.array(features)

# Using Skicit-learn to split data into training and testing sets
from sklearn.model_selection import train_test_split

# Split the data into training and testing sets
train, test, train_labels, test_labels = train_test_split(features, labels, test_size=0.25,
                                                          random_state=42)

print('Training Features Shape:', train.shape)
print('Training Labels Shape:', train_labels.shape)
print('Testing Features Shape:', test.shape)
print('Testing Labels Shape:', test_labels.shape)
print(test_labels)

train = train.astype('bool')
train_labels = train_labels.astype('bool')
test = test.astype('bool')
test_labels = test_labels.astype('bool')

# Import the model we are using
from sklearn.ensemble import RandomForestClassifier

# Instantiate model with 1000 decision trees
rf = RandomForestClassifier(n_estimators=1000, random_state=42)
# Train the model on training data
rf.fit(train, train_labels)

# Use the forest's predict method on the test data
predictions = rf.predict(test)
print(predictions)
# Calculate the absolute errors
errors = abs(predictions ^ test_labels)
print(errors)

'''
# Print out the mean absolute error (mae)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')

# Calculate mean absolute percentage error (MAPE)
mape = 100 * Paid_rate_division(errors, test_labels.all())
# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', round(accuracy, 2), '%.')
'''
n_nodes = []

max_depths = []

# Stats about the trees in random forest
for ind_tree in rf.estimators_:
    n_nodes.append(ind_tree.tree_.node_count)
    max_depths.append(ind_tree.tree_.max_depth)

print(f'Average number of nodes {int(np.mean(n_nodes))}')
print(f'Average maximum depth {int(np.mean(max_depths))}')

# Training predictions (to demonstrate overfitting)
train_rf_predictions = rf.predict(train)
train_rf_probs = rf.predict_proba(train)[:, 1]

# Testing predictions (to determine performance)
rf_predictions = rf.predict(test)
rf_probs = rf.predict_proba(test)[:, 1]

from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# Plot formatting
plt.style.use('fivethirtyeight')
plt.rcParams['font.size'] = 18


def evaluate_model(predictions, probs, train_predictions, train_probs):
    """Compare machine learning model to baseline performance.
    Computes statistics and shows ROC curve."""

    baseline = {}

    baseline['recall'] = recall_score(test_labels,
                                      [1 for _ in range(len(test_labels))])
    baseline['precision'] = precision_score(test_labels,
                                            [1 for _ in range(len(test_labels))])
    baseline['roc'] = 0.5

    results = {}

    results['recall'] = recall_score(test_labels, predictions)
    results['precision'] = precision_score(test_labels, predictions)
    results['roc'] = roc_auc_score(test_labels, probs)

    train_results = {}
    train_results['recall'] = recall_score(train_labels, train_predictions)
    train_results['precision'] = precision_score(train_labels, train_predictions)
    train_results['roc'] = roc_auc_score(train_labels, train_probs)

    for metric in ['recall', 'precision', 'roc']:
        print(
            f'{metric.capitalize()} Baseline: {round(baseline[metric], 2)} Test: {round(results[metric], 2)} Train: {round(train_results[metric], 2)}')

    # Calculate false positive rates and true positive rates
    base_fpr, base_tpr, _ = roc_curve(test_labels, [1 for _ in range(len(test_labels))])
    model_fpr, model_tpr, _ = roc_curve(test_labels, probs)

    plt.figure(figsize=(8, 6))
    plt.rcParams['font.size'] = 16

    # Plot both curves
    plt.plot(base_fpr, base_tpr, 'b', label='baseline')
    plt.plot(model_fpr, model_tpr, 'r', label='model')
    plt.legend();
    plt.xlabel('False Positive Rate');
    plt.ylabel('True Positive Rate');
    plt.title('ROC Curves');
    plt.show();


evaluate_model(rf_predictions, rf_probs, train_rf_predictions, train_rf_probs)
plt.savefig('roc_auc_curve.png')

from sklearn.metrics import confusion_matrix
import itertools


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Oranges):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    Source: http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    # Plot the confusion matrix
    plt.figure(figsize=(10, 10))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, size=24)
    plt.colorbar(aspect=4)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, size=14)
    plt.yticks(tick_marks, classes, size=14)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.

    # Labeling the plot
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), fontsize=20,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.grid(None)
    plt.tight_layout()
    plt.ylabel('True label', size=18)
    plt.xlabel('Predicted label', size=18)


# Confusion matrix
cm = confusion_matrix(test_labels, rf_predictions)
plot_confusion_matrix(cm, classes=['Poor Health', 'Good Health'],
                      title='Health Confusion Matrix')

plt.savefig('cm.png')
