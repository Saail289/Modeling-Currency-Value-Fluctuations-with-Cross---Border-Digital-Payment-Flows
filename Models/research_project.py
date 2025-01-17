# -*- coding: utf-8 -*-
"""Research_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Kl9fQz90c15bKRKl41oV7UWgS8GSSFwD

## **DKRVFLN-AE**
"""

!pip install pandas numpy scikit-learn tensorflow matplotlib openpyxl

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt

# Load the Forex Dataset
file_path = '/content/All_Countries.xlsx'  # Update this if file path changes
sheet_name = 'Sheet1'  # Adjust sheet name if needed
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Display basic info about the data
print("Dataset Preview:")
print(df.head(10))
print("\nColumns:", df.columns)

# User Input for Index to Predict
target_column = input("Enter the name of the column to predict: ").strip()

# Verify if the column exists
if target_column not in df.columns:
    raise ValueError(f"Column '{target_column}' not found in the dataset!")

# Preprocessing the Data
# Drop rows with missing values
df = df.dropna()

# Convert the 'date_column' to datetime format (replace 'date_column' with your actual column name)
df['observation_date'] = pd.to_datetime(df['observation_date'], format='%d-%m-%Y', errors='coerce')

# Drop rows with invalid dates if any
df = df.dropna(subset=['observation_date'])

# Extract numerical features from the date
df['year'] = df['observation_date'].dt.year
df['month'] = df['observation_date'].dt.month
df['day'] = df['observation_date'].dt.day
df['day_of_week'] = df['observation_date'].dt.dayofweek

# Drop the original 'date_column' as it's no longer needed
df = df.drop(columns=['observation_date'])

# Feature Selection
X = df.drop(columns=[target_column])
y = df[target_column]

# Identify numeric columns in X
numeric_columns = X.select_dtypes(include=['number']).columns
print(f"Numeric Columns for Scaling: {list(numeric_columns)}")

# Filter numeric columns for scaling
X_numeric = X[numeric_columns]

# Scale the data
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X_numeric)

scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

# Define the DKRVFLN-AE Model
def build_DKRVFLN_AE(input_dim):
    # Encoder
    input_layer = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(128, activation='relu')(input_layer)
    encoded = layers.Dense(64, activation='relu')(encoded)
    encoded = layers.Dense(32, activation='relu')(encoded)

    # Decoder
    decoded = layers.Dense(64, activation='relu')(encoded)
    decoded = layers.Dense(128, activation='relu')(decoded)
    decoded = layers.Dense(input_dim, activation='sigmoid')(decoded)

    # Autoencoder Model
    autoencoder = models.Model(inputs=input_layer, outputs=decoded)

    # Extract Encoder Part
    encoder = models.Model(inputs=input_layer, outputs=encoded)

    # Compile Autoencoder
    autoencoder.compile(optimizer='adam', loss='mse')

    # Random Vector Functional Link Layer
    rfl_layer = models.Sequential([
        layers.Dense(256, activation='relu', input_shape=(32,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(1, activation='linear')
    ])

    # Full DKRVFLN-AE Model
    input_data = layers.Input(shape=(input_dim,))
    encoded_features = encoder(input_data)
    output = rfl_layer(encoded_features)

    final_model = models.Model(inputs=input_data, outputs=output)
    final_model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    return autoencoder, final_model

# Build the Model
autoencoder, dkrvfln_ae_model = build_DKRVFLN_AE(X_train.shape[1])

# Train the Autoencoder
print("Training Autoencoder...")
autoencoder.fit(X_train, X_train, epochs=50, batch_size=32, validation_data=(X_test, X_test), verbose=1)

# Train the DKRVFLN-AE Model
print("\nTraining DKRVFLN-AE Model...")
history = dkrvfln_ae_model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), verbose=1)

# Predictions
y_pred_scaled = dkrvfln_ae_model.predict(X_test)
y_pred = scaler_y.inverse_transform(y_pred_scaled)
y_test_actual = scaler_y.inverse_transform(y_test)

# Evaluation Metrics
mae = mean_absolute_error(y_test_actual, y_pred)
rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred))
r2 = r2_score(y_test_actual, y_pred)

print("\nModel Evaluation:")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"R² Score: {r2:.4f}")

# Plotting Actual vs Predicted Values
plt.figure(figsize=(10, 6))
plt.plot(y_test_actual, label='Actual Values', color='b')
plt.plot(y_pred, label='Predicted Values', color='r', linestyle='dashed')
plt.title('Actual vs Predicted Values')
plt.xlabel('Sample')
plt.ylabel('Target Value')
plt.legend()
plt.show()

# User Prediction for Custom Input
print("\nEnter new data for prediction:")
new_data = []
for column in X.columns:
    value = float(input(f"Enter value for {column}: "))
    new_data.append(value)

new_data_scaled = scaler_X.transform([new_data])
predicted_value_scaled = dkrvfln_ae_model.predict(new_data_scaled)
predicted_value = scaler_y.inverse_transform(predicted_value_scaled)

print(f"\nPredicted Value for the Target Column '{target_column}': {predicted_value[0][0]:.4f}")

# Normalize Data
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

# Split Data into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

"""# **EMD-LSTM**"""

!pip install EMD-signal

from PyEMD import EMD  # For Empirical Mode Decomposition

# Step 1: Apply EMD to Decompose the Target Variable into IMFs
emd = EMD()
IMFs = emd.emd(y_train.ravel())  # Decomposing the training target variable

print(f"Number of IMFs: {len(IMFs)}")

# Train-Test Split
train_size = int(len(X_scaled) * 0.8)
X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
IMFs_train, IMFs_test = IMFs[:, :train_size], IMFs[:, train_size:]

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# LSTM Model Training for Each IMF
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, activation='tanh', return_sequences=False, input_shape=input_shape))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

imf_predictions = []
for i, imf in enumerate(IMFs):
    print(f"Training LSTM for IMF-{i+1}")
    y_train = imf[:train_size].reshape(-1, 1)
    y_test = imf[train_size:].reshape(-1, 1)

    # Reshape for LSTM
    X_train_lstm = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test_lstm = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    # Train LSTM
    lstm_model = create_lstm_model((X_train_lstm.shape[1], X_train_lstm.shape[2]))
    lstm_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)

    # Predict
    y_pred_imf = lstm_model.predict(X_test_lstm)
    imf_predictions.append(y_pred_imf.flatten())

# Combine Predictions of All IMFs
final_prediction = np.sum(imf_predictions, axis=0)

# Inverse Transform Prediction
y_pred_final = scaler_y.inverse_transform(final_prediction.reshape(-1, 1))
y_actual = scaler_y.inverse_transform(y_scaled[train_size:].reshape(-1, 1))

# Evaluation Metrics
mae = mean_absolute_error(y_actual, y_pred_final)
rmse = np.sqrt(mean_squared_error(y_actual, y_pred_final))
r2 = r2_score(y_actual, y_pred_final)

print("\nModel Evaluation:")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"R² Score: {r2:.4f}")

# Plot Results
plt.figure(figsize=(10, 6))
plt.plot(y_actual, label="Actual", color="blue")
plt.plot(y_pred_final, label="Predicted", color="red")
plt.title("EMD-LSTM Model Predictions")
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()
plt.show()

"""### **ICA-LSTM-PSO**"""

!pip install scikit-learn keras tensorflow PySwarms

from sklearn.decomposition import FastICA
import pyswarms as ps
from pyswarms.utils.functions import single_obj as fx

# Normalize the data
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42, shuffle=False)

# Step 3: Apply ICA to decompose the features
n_components = min(X_train.shape[1], 5)  # Choose the number of independent components
ica = FastICA(n_components=n_components, random_state=42)
X_train_ica = ica.fit_transform(X_train)
X_test_ica = ica.transform(X_test)

# Step 4: Define the LSTM model
def create_lstm_model(params):
    """ Creates an LSTM model using hyperparameters from PSO. """
    lstm_units, dense_units, learning_rate = int(params[0]), int(params[1]), params[2]

    model = Sequential()
    model.add(LSTM(lstm_units, activation='tanh', input_shape=(X_train_ica.shape[1], 1)))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                  loss='mean_squared_error')
    return model

def objective_function(params):
    """ Objective function for PSO to minimize LSTM validation loss. """
    losses = []  # To store the loss for each particle

    # Iterate through each particle
    for i in range(params.shape[0]):
        lstm_units = int(max(5, min(params[i, 0], 100)))
        dense_units = int(max(5, min(params[i, 1], 100)))
        learning_rate = max(1e-5, min(params[i, 2], 0.01))

        # Reshape data for LSTM
        X_train_lstm = X_train_ica.reshape((X_train_ica.shape[0], X_train_ica.shape[1], 1))
        X_test_lstm = X_test_ica.reshape((X_test_ica.shape[0], X_test_ica.shape[1], 1))

        # Create and train the LSTM model
        model = Sequential()
        model.add(LSTM(lstm_units, activation='tanh', input_shape=(X_train_ica.shape[1], 1)))
        model.add(Dense(1, activation='linear'))
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                      loss='mean_squared_error')

        # Train the model (silent mode)
        model.fit(X_train_lstm, y_train, epochs=10, batch_size=32, verbose=0, validation_split=0.2)

        # Evaluate model on validation set
        loss = model.evaluate(X_test_lstm, y_test, verbose=0)
        losses.append(loss)

    return np.array(losses)  # Return losses for all particles

# Step 6: Perform PSO to optimize LSTM hyperparameters
# Hyperparameter ranges: [lstm_units, dense_units, learning_rate]
lb = [10, 10, 0.0001]  # Lower bounds
ub = [100, 100, 0.01]  # Upper bounds

# Initialize PSO optimizer
optimizer = ps.single.GlobalBestPSO(n_particles=10, dimensions=3, options={'c1': 0.5, 'c2': 0.3, 'w': 0.9},
                                    bounds=(lb, ub))

# Run optimization
best_cost, best_params = optimizer.optimize(objective_function, iters=5)
print("Best Hyperparameters (LSTM Units, Dense Units, Learning Rate):", best_params)

# Step 7: Train LSTM with optimized parameters
lstm_units, dense_units, learning_rate = int(best_params[0]), int(best_params[1]), best_params[2]
final_model = create_lstm_model([lstm_units, dense_units, learning_rate])

# Reshape data for LSTM
X_train_lstm = X_train_ica.reshape((X_train_ica.shape[0], X_train_ica.shape[1], 1))
X_test_lstm = X_test_ica.reshape((X_test_ica.shape[0], X_test_ica.shape[1], 1))

# Train final model
final_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=1)

# Step 8: Make predictions
y_pred = final_model.predict(X_test_lstm)
y_pred_rescaled = scaler_y.inverse_transform(y_pred)
y_test_rescaled = scaler_y.inverse_transform(y_test)

print("Shape of y_test_rescaled:", y_test_rescaled.shape)
print("Shape of y_pred_rescaled:", y_pred_rescaled.shape)

# Step 9: Evaluate the model
mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
rmse = np.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))
r2 = r2_score(y_test_rescaled, y_pred_rescaled)

print("\nModel Evaluation Metrics:")
print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"R² Score: {r2:.4f}")

