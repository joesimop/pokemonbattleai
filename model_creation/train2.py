import logging
import urllib.request
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from keras.models import Model, load_model
from keras.layers import Input, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam


def encode_moves(df, move_list):
    # Assume 'move_list' is a list of all unique moves available to all Pokémon
    encoder = OneHotEncoder(categories=[move_list], sparse=False)
    # Reshape is necessary if 'PlayerMove' is a 1D array (series)
    encoded_moves = encoder.fit_transform(df['PlayerMove'].values.reshape(-1, 1))
    return encoded_moves, encoder


def get_moves_from_excel(file_path):
    # Load the Excel file
    moves_data = pd.ExcelFile(file_path)
    # Read the first sheet or a specific sheet if required
    moves_df = pd.read_excel(moves_data, sheet_name=0)
    # Assume that the first column contains the moves; adjust if it's a different column
    moves_list = moves_df.iloc[:, 0].unique().tolist()
    # Sort the list if the moves are numerical
    if all(isinstance(move, (int, float)) for move in moves_list):
        moves_list.sort()
    return moves_list


def train2(turnTable, model_name):
    # data = pd.ExcelFile('turns.csv')
    # df = pd.read_excel(data, sheet_name=0)
    df = pd.read_csv(turnTable)

    move_list = get_moves_from_excel('moves.xlsx')

    # Encode the moves
    Y, move_encoder = encode_moves(df, move_list)

    # Features
    X = df.drop(columns=['PlayerMove'])

    # Split into training and test sets
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    # Normalize features
    scaler_X = MinMaxScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)

    # Model definition
    input_layer = Input(shape=(X_train_scaled.shape[1],))

    # First hidden layer
    hidden_layer_1 = Dense(256, activation='relu')(input_layer)
    hidden_layer_1 = BatchNormalization()(hidden_layer_1)
    hidden_layer_1 = Dropout(0.3)(hidden_layer_1)

    # Second hidden layer
    hidden_layer_2 = Dense(256, activation='relu')(hidden_layer_1)
    hidden_layer_2 = BatchNormalization()(hidden_layer_2)
    hidden_layer_2 = Dropout(0.3)(hidden_layer_2)

    # Third hidden layer
    hidden_layer_3 = Dense(256, activation='relu')(hidden_layer_2)
    hidden_layer_3 = BatchNormalization()(hidden_layer_3)
    hidden_layer_3 = Dropout(0.3)(hidden_layer_3)

    # Fourth hidden layer
    hidden_layer_4 = Dense(128, activation='relu')(hidden_layer_3)
    hidden_layer_4 = BatchNormalization()(hidden_layer_4)
    hidden_layer_4 = Dropout(0.3)(hidden_layer_4)

    # Fifth hidden layer
    hidden_layer_5 = Dense(64, activation='relu')(hidden_layer_4)

    # Output layer
    output_layer = Dense(len(move_list), activation='softmax')(hidden_layer_5)

    # Create the model
    model = Model(inputs=input_layer, outputs=output_layer)

    # (learning_rate=0.001) PUT THIS IN BUT TEST WITHOUT
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # Calculate class weights
    # Assign lower weight to 'switch' move (ID 0) and higher weights to other moves
    class_weights = {0: 0.125}  # Start by giving a low weight to the 'switch' class
    for move_id in range(1, len(move_list)):
        class_weights[move_id] = 1  # Assign normal weight to other moves

    # Train the model with class weights
    model.fit(X_train_scaled, Y_train, epochs=10, batch_size=32,
              validation_data=(X_test_scaled, Y_test), class_weight=class_weights)

    # Evaluate the model on the test set
    model.evaluate(X_test_scaled, Y_test)

    model.save(model_name)
