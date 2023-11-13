import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from keras.models import load_model
import numpy as np


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


def test_model():
    model = load_model('pokemon_model.h5')

    # df = pd.read_csv('turns.csv')
    df = pd.read_excel('test.xlsx')

    move_list = get_moves_from_excel('moves.xlsx')

    # Encode the moves
    Y_test, move_encoder = encode_moves(df, move_list)

    # Features
    X_test = df.drop(columns=['PlayerMove'])

    # Normalize features
    scaler_X = MinMaxScaler()
    # X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.fit_transform(X_test)

    # Make predictions on the test set
    predictions = model.predict(X_test_scaled)

    # Get the indices of the top N probabilities, here N=10
    top_n_indices = np.argpartition(predictions, -50, axis=1)[:, -50:]

    # Assuming move_encoder.categories_ contains the array of all possible moves
    all_possible_moves = move_encoder.categories_[0]

    # Map the predicted move indices to actual move names using the categories
    predicted_moves_n = [all_possible_moves[top_n_indices[:, -i - 1]] for i in range(50)]

    # If Y_test is one-hot encoded, convert it back to move IDs and then to move names
    actual_move_ids = np.argmax(Y_test, axis=1)
    actual_moves = all_possible_moves[actual_move_ids]

    # Output the comparison of each turn's predicted vs actual move
    total = 0
    count = 0
    for i in range(len(actual_moves)):
        predicted_for_turn = [predicted[i] for predicted in predicted_moves_n]  # Initialize before the if statement

        if actual_moves[i] != 0:
            if actual_moves[i] in predicted_for_turn:
                count += 1
            if 835 in predicted_for_turn or 460 in predicted_for_turn or \
                    743 in predicted_for_turn or 401 in predicted_for_turn:
                print("pog")
            total += 1
        print(f"Turn {i + 1}: Actual Move - {actual_moves[i]}, Predicted Moves - {predicted_for_turn}")

    accuracy = count / total if total > 0 else 0
    print(f"Accuracy within top 50 predictions: {accuracy:.2f}")
    print(count)
    print(str(accuracy))
    