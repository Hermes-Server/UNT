#!/bin/bash

#
# Subscription test
#
./coord_deleteAllSubscriptions &> deleteSub.out
./coord_postSubscription testSubscription.json &> postSub.out
./coord_getSubscriptions &> getSub.out
