from Base.Recommender_utils import check_matrix
import numpy as np


class LinearHybridRecommender:
    """ LinearHybridRecommender
    Hybrid of two prediction scores R = R1*alpha + R2*(1-alpha)

    """

    RECOMMENDER_NAME = "LinearHybridRecommender"

    def __init__(self, URM_train, ItemCFKNN, RP3beta, SLIMElasticNet, ItemCBF, UserCFKNN):
        super(LinearHybridRecommender, self).__init__()
        self.URM_train = check_matrix(URM_train.copy(), 'csr')

        self.ItemCFKNN = ItemCFKNN
        self.RP3beta = RP3beta
        self.SLIMElasticNet = SLIMElasticNet
        self.ItemCBF = ItemCBF
        self.UserCFKNN = UserCFKNN

        # i think this following line is pretty useless.
        # self.compute_item_score = self.compute_scores_hybrid

    def fit(self, ItemCFKNN_weight=1.0, RP3beta_weight=1.0, SLIMElasticNet_weight=1.0, ItemCBF_weight=1.0, UserCFKNN_weight=1.0, retrain_all_algorithms=False):
        if retrain_all_algorithms:
            self.ItemCFKNN.fit()
            self.RP3beta.fit()
            self.SLIMElasticNet.fit()
            self.ItemCBF.fit()
            self.UserCFKNN.fit()

        print("[LinearHybridRecommender] Fitting with parameters: ItemCFKNN_weight={}, RP3beta_weight={}, SLIMElasticNet_weight={}, ItemCBF_weight={}, UserCFKNN_weight={}"
              .format(ItemCFKNN_weight, RP3beta_weight, SLIMElasticNet_weight, ItemCBF_weight, UserCFKNN_weight))

        self.ItemCFKNN_weight = ItemCFKNN_weight
        self.RP3beta_weight = RP3beta_weight
        self.SLIMElasticNet_weight = SLIMElasticNet_weight
        self.ItemCBF_weight = ItemCBF_weight
        self.UserCFKNN_weight = UserCFKNN_weight

    def compute_scores_hybrid(self, user_id):
        item_scores_ItemCFKNN = self.ItemCFKNN.compute_score(user_id)
        item_scores_RP3beta = self.RP3beta.compute_score(user_id)
        item_scores_SLIMElasticNet = self.SLIMElasticNet.compute_score(user_id)
        item_scores_ItemCBF = self.ItemCBF.compute_score(user_id)
        item_scores_UserCFKNN = self.UserCFKNN.compute_score(user_id)

        item_scores_weighted = item_scores_ItemCFKNN * self.ItemCFKNN_weight + \
                               item_scores_RP3beta * self.RP3beta_weight + \
                               item_scores_SLIMElasticNet * self.SLIMElasticNet_weight + \
                               item_scores_ItemCBF * self.ItemCBF_weight + \
                               item_scores_UserCFKNN * self.UserCFKNN_weight

        return item_scores_weighted

    def recommend(self, user_id, at=10, exclude_seen=True):
        scores = self.compute_scores_hybrid(user_id)

        if exclude_seen:
            scores = self.filter_seen(user_id, scores)

        # rank items
        ranking = scores.argsort()[::-1]

        return ranking[:at]

    def filter_seen(self, user_id, scores):

        start_pos = self.URM_train.indptr[user_id]
        end_pos = self.URM_train.indptr[user_id + 1]

        user_profile = self.URM_train.indices[start_pos:end_pos]

        scores[user_profile] = -np.inf

        return scores
