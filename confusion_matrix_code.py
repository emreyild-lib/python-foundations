# confusion_matrix_example.py
# pip install scikit-learn
from sklearn.metrics import confusion_matrix
from sklearn.metrics import recall_score
import numpy as np
# ---- Step 1: True labels (actual answers) ----
# Suppose we have 8 test cases for a binary classification (Yes=1, No=0)
y_true = [1, 0, 1, 1, 0, 1, 0, 0]
# ---- Step 2: Predicted labels (model’s guesses) ----
y_pred = [1, 0, 1, 0, 0, 1, 1, 0]
# ---- Step 3: Make confusion matrix ----
cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:")
print(cm)

precison= precison_score(y_true, y_pred) * 100
recall = recall_score(y_true, y_pred)
print('Recall:', recall)