from Base.Similarity.Compute_Similarity_Python import Compute_Similarity_Python
import scipy.sparse as sps
import numpy as np
from DataUtils.ParserURM import ParserURM
from DataUtils.ouputGenerator import *
from Notebooks_utils.evaluation_function import evaluate_algorithm_original


class UserCFKNNRecommender(object):

    def __init__(self, URM):
        self.URM = URM

    def fit(self, topK=10, shrink=0.5, normalize=False, similarity="jaccard"):
        print("[UserCFKNN] Fitting model with parameters: topK={}, shrink={}, similarity={}".format(topK, shrink, similarity))

        similarity_object = Compute_Similarity_Python(self.URM.T, shrink=shrink,
                                                      topK=topK, normalize=normalize,
                                                      similarity=similarity)

        self.W_sparse = similarity_object.compute_similarity()

    def compute_score(self, user_id, exclude_seen=False):
        scores = self.W_sparse[user_id, :].dot(self.URM).toarray().ravel()

        if exclude_seen:
            scores = self.filter_seen(user_id, scores)

        return scores

    def recommend(self, user_id, at=None, exclude_seen=True):
        # compute the scores using the dot product
        scores = self.W_sparse[user_id, :].dot(self.URM).toarray().ravel()

        if exclude_seen:
            scores = self.filter_seen(user_id, scores)

        # rank items
        ranking = scores.argsort()[::-1]

        return ranking[:at]

    def filter_seen(self, user_id, scores):
        start_pos = self.URM.indptr[user_id]
        end_pos = self.URM.indptr[user_id + 1]

        user_profile = self.URM.indices[start_pos:end_pos]

        scores[user_profile] = -np.inf

        return scores

    def save_model(self, name, path = "C:/Users/Utente/Desktop/RecSys-Competition-2019/recommenders/models/UserCFKNN"):
        print("[UserCFKNN] Saving model on file " + path + "/" + name + ".npz")
        sps.save_npz(path + "/" + name + ".npz", self.W_sparse, compressed=True)

    def load_model(self, name, path = "C:/Users/Utente/Desktop/RecSys-Competition-2019/recommenders/models/UserCFKNN"):
        print("[UserCFKNN] Loading model from file " + path + "/" + name + ".npz")
        self.W_sparse = sps.load_npz(path + "/" + name + ".npz")
        print("[UserCFKNN] Model loaded correctly")
        self.W_sparse = self.W_sparse.tocsr()

    def get_model(self):
        return self.W_sparse

