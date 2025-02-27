import os
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from tensorflow.python.keras.api._v1.keras.models import Sequential
from tensorflow.python.keras.api._v1.keras.layers import Dense, Dropout, LSTM, Flatten, Bidirectional
from tensorflow.python.keras.api._v1.keras.layers import Convolution1D, MaxPooling1D
from tensorflow.python.keras.api._v1.keras import backend as K
from tensorflow.python.keras.api._v1.keras.wrappers.scikit_learn import KerasClassifier
import warnings
from contextlib import redirect_stdout

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
# export CUDA_VISIBLE_DEVICES='0'
np.random.seed(1234)


def to_excel(history, filename):
    history.history["epoch"] = history.epoch
    dfData = history.history
    df = pd.DataFrame(dfData)
    df.to_excel(filename, index=False)


def to_excel_yhat(y_test, yhat, name):
    y_test = [np.argmax(i) for i in y_test]
    yhat = yhat.tolist()
    column1, column2 = ["Ytest"], ["Yhat"]
    dt1 = pd.DataFrame(y_test, columns=column1)
    dt2 = pd.DataFrame(yhat, columns=column2)
    dt = pd.concat([dt1, dt2], axis=1)
    dt.to_excel(name, index=0)


# 2 Define precision
def precision(y_true, y_pred):
    tp = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))  # true positives
    pp = K.sum(K.round(K.clip(y_pred, 0, 1)))  # predicted positives
    precision = tp / (pp + K.epsilon())
    return precision


# 3 Define recall
def recall(y_true, y_pred):
    tp = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))  # true positives
    pp = K.sum(K.round(K.clip(y_true, 0, 1)))  # possible positives
    recall = tp / (pp + K.epsilon())
    return recall


# 4 Define F1-score
def f1(y_true, y_pred):
    precision_ = precision(y_true, y_pred)
    recall_ = recall(y_true, y_pred)
    f1 = 2 * ((precision_ * recall_) / (precision_ + recall_ + K.epsilon()))
    return f1


# 5 Define FireLoc to value Mapping
def MapLoc(key):
    global ValueKey
    ValueKey = dict([('70M', 1), ('70U', 2), ('100M', 3), ('100U', 4), ('130M', 5), ('130U', 6)])
    return ValueKey.get(key)


# LOC Define normalization coder
def MinMaxSC(data):
    scaler = MinMaxScaler()
    scaler = scaler.fit(data)
    result = scaler.transform(data)
    result = pd.DataFrame(result)
    return result


# 7 Define one-hot coder
def OneHotSc(data):
    enc = OneHotEncoder()
    enc = enc.fit(data)
    result = enc.transform(data).toarray()
    result = pd.DataFrame(result)
    return result


# Define BPNN model
def BPNN_model():
    model = Sequential()
    model.add(Dense(200, activation='relu', input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])

    return model


# 9  Define CNN model
def CNN_model():
    model = Sequential()
    model.add(Convolution1D(filters=200, kernel_size=3, strides=1, padding='same',
                            activation='relu', input_shape=(X.shape[1], X.shape[2])))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Convolution1D(filters=100, kernel_size=3, strides=1, padding='same',
                            activation='relu'))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])

    return model


# 10 Define CNN-LSTM model
def CNN_LSTM_model():
    model = Sequential()
    model.add(Convolution1D(filters=200, kernel_size=3, strides=1, padding='same',
                            activation='relu', input_shape=(X.shape[1], X.shape[2])))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Convolution1D(filters=100, kernel_size=3, strides=1, padding='same',
                            activation='relu'))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Dropout(0.2))
    model.add(LSTM(100, return_sequences=True))
    model.add(Dropout(0.1))
    model.add(LSTM(10))
    model.add(Dropout(0.1))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])

    return model


# 11 Define LSTM model
def LSTM_model():
    model = Sequential()
    model.add(LSTM(
        input_shape=(X.shape[1], X.shape[2]),
        units=100,
        return_sequences=True))
    model.add(Dropout(0.1))
    model.add(LSTM(
        units=20,
        return_sequences=False))
    model.add(Dropout(0.1))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])

    return model


def BILSTM_model():
    model = Sequential()
    model.add(Bidirectional(LSTM(
        units=100,
        return_sequences=True),
        input_shape=(X.shape[1], X.shape[2]), ))

    model.add(Dropout(0.1))
    model.add(Bidirectional(LSTM(
        units=20,
        return_sequences=False)))
    model.add(Dropout(0.1))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])
    return model


def CNN_BILSTM_model():
    model = Sequential()
    model.add(Convolution1D(filters=200, kernel_size=3, strides=1, padding='same',
                            activation='relu', input_shape=(X.shape[1], X.shape[2])))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Convolution1D(filters=100, kernel_size=3, strides=1, padding='same',
                            activation='relu'))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Dropout(0.2))
    model.add(Bidirectional(LSTM(
        units=100,
        return_sequences=True),
        input_shape=(X.shape[1], X.shape[2]), ))

    model.add(Dropout(0.1))
    model.add(Bidirectional(LSTM(
        units=20,
        return_sequences=False)))
    model.add(Dropout(0.1))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', precision, recall, f1])
    return model


# 12 Define init dataSets
InitPreDf = pd.DataFrame()
InitPreLabelLoc = []
InitPreLabelDam = []


# 13 run models
def run(model, t, name, cate):
    tic = time.perf_counter()
    model = KerasClassifier(build_fn=model, verbose=0)
    print(model.build_fn().summary())
    with open('D:\code\Fire\PLOT\SUMMARY\summary' + name + '_' + cate + '_' + t + '-' + str(slide) + '.txt', 'w') as f:
        with redirect_stdout(f):
            model.build_fn().summary()
    print(X.shape, y.shape)
    history = model.fit(X, y, epochs=500, batch_size=128, validation_split=0.25, verbose=1)
    toc = time.perf_counter()
    y_hat = model.predict(X_test)
    to_excel(history, 'D:\code\FIRE\RESULTS\\' + name + '_' + cate + '_' + t + '-' + str(slide) + '.xlsx')
    to_excel_yhat(y_test, y_hat, 'D:\code\FIRE\RESULTS\\' + name + '_' + cate + '_' + t + '-' + str(slide) + 'hat.xlsx')
    time_str = f"{toc - tic:0.4f}"
    print(time_str)
    with open('D:\code\Fire\PLOT\RUNTIME\\time' + name + '_' + cate + '_' + t + '-' + str(slide) + '.txt', 'w') as f:
        with redirect_stdout(f):
            print(time_str)


# 14 Data processing and data set division
def DataProcess(slide, t):
    InitArrayDf = np.load(r'./DATASET/InitArrayDf' + t + '-' + str(slide) + '21' + '.npy',
                          allow_pickle=True)

    InitArrayLabelLoc = np.load(
        r'./DATASET/InitArrayLabelLoc' + t + '-' + str(slide) + '21' + '.npy',
        allow_pickle=True)
    InitArrayLabelDam = np.load('./DATASET/InitArrayLabelDam' + t + '-' + str(slide) +
                                '21' + '.npy',
                                allow_pickle=True)


    X_pre_soot = MinMaxSC(InitArrayDf)

    y_pre_loc = OneHotSc(InitArrayLabelLoc.reshape(-1, 1))
    y_pre_dam = OneHotSc(InitArrayLabelDam.reshape(-1, 1))

    X_pre_data = X_pre_soot

    X_, y_loc, y_dam = np.array(X_pre_data), np.array(y_pre_loc), np.array(y_pre_dam)
    X = X_.reshape(int(X_.shape[0] / slide), int(slide), int(X_.shape[1]))
    index = [i for i in range(len(X))]
    np.random.shuffle(index)
    X = X[index]
    y_loc = y_loc[index]
    y_dam = y_dam[index]
    #
    test_ratio = 0.20
    y_loc_test = y_loc[:int(test_ratio * y_loc.shape[0])]
    y_dam_test = y_dam[:int(test_ratio * y_dam.shape[0])]
    X_test = X[:int(test_ratio * X.shape[0])]
    y_loc = y_loc[int(test_ratio * y_loc.shape[0]):]
    y_dam = y_dam[int(test_ratio * y_dam.shape[0]):]
    X = X[int(test_ratio * X.shape[0]):]
    return X, X_test, y_loc, y_loc_test, y_dam, y_dam_test


#
#
# select duration of fire
totle_ = 300
# select time window
slide = 30
# select task type :
# '6' refer to fire location detection task
# '32' refer to damper combination detection task
cate = '32'
#
#
X, X_test, y_loc, y_loc_test, y_dam, y_dam_test = DataProcess(slide, str(totle_))
#
if cate == '32':
    y = y_dam
    y_test = y_dam_test
if cate == '6':
    y = y_loc
    y_test = y_loc_test
# 15 Main process
# choices the model 'BPNN','CNN','LSTM','BILSTM','CNN-BILSTM','CNN-LSTM'
run(CNN_BILSTM_model, str(totle_), 'BILSTM', cate)
