import securexgboost as xgb
import os

username = "user1"
DIR = os.path.dirname(os.path.realpath(__file__))
HOME_DIR = DIR + "/../../../"
sym_key_file = DIR + "/../../data/key_zeros.txt"
priv_key_file = DIR + "/../../../config/user1.pem"
cert_file = DIR + "/../../../config/user1.crt"


print("Init user and enclave parameters")
xgb.init_client(user_name=username, sym_key_file=sym_key_file, priv_key_file=priv_key_file, cert_file=cert_file)
xgb.init_server(enclave_image=HOME_DIR + "build/enclave/xgboost_enclave.signed", log_verbosity=3)

# Remote Attestation
print("Remote attestation")

# Note: Simulation mode does not support attestation
# pass in `verify=False` to attest()
xgb.attest(verify=False)

print("Creating training matrix from encrypted file")
dtrain = xgb.DMatrix({username: HOME_DIR + "demo/data/agaricus.txt.train.enc"})

print("Creating test matrix from encrypted file")
dtest = xgb.DMatrix({username: HOME_DIR + "demo/data/agaricus.txt.test.enc"})

print("Beginning Training")
# Set training parameters
params = {
        "tree_method": "hist",
        "n_gpus": "0",
        "objective": "binary:logistic",
        "min_child_weight": "1",
        "gamma": "0.1",
        "max_depth": "3",
        "verbosity": "3" 
}

# Train and evaluate
num_rounds = 5 
booster = xgb.train(params, dtrain, num_rounds, evals=[(dtrain, "train"), (dtest, "test")])

print("Saving model")
# Save model to a file
booster.save_model(HOME_DIR + "demo/python/basic/modelfile.model")

print("Loading model")
# Load model from file
booster = xgb.Booster()
booster.load_model(HOME_DIR + "demo/python/basic/modelfile.model")

# Get encrypted predictions
print("\nModel Predictions: ")
predictions, num_preds = booster.predict(dtest, decrypt=False)

# Decrypt predictions
print(booster.decrypt_predictions(predictions, num_preds))

# Get fscores of model
print("\nModel Feature Importance: ")
print(booster.get_fscore())
