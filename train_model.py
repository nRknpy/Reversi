from sklearn.neural_network import MLPClassifier
import numpy as np
import pickle

train_x=np.load("train_x.npy")
train_y=np.load("train_y.npy")

print(train_x.shape)
print(train_y.shape)

model=MLPClassifier(hidden_layer_sizes=(128,64),batch_size=100,random_state=1,verbose=2,early_stopping=True)
model.fit(train_x,train_y)

with open('mlp_model', 'wb') as f:
    pickle.dump(model, f)

test_x = np.array([[
[[0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,1,0,0,0],
 [0,0,0,1,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0]],

[[0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,1,0,0,0,0],
 [0,0,0,0,1,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0]]]],dtype=np.int8)

test_x=np.reshape(test_x,[-1,128])
test_y=model.predict_proba(test_x)
test_y=np.insert(test_y,27,[-1,-1])
test_y=np.insert(test_y,35,[-1,-1])
print(test_y)
pos=np.argmax(test_y)
print(pos)
print(test_y[pos])