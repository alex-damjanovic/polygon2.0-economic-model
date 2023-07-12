"""
# Supernets

The number of supernets will progressively increase over time, as the more consumers adopting Polygon.
The supernets will be divided into public and private chains, big and small businesses.
"""

import typing

import model.constants as constants
import numpy as np

def policy_new_supernet_staking(
    params, substep, state_history, previous_state
) -> typing.Dict[str, any]:
    # Parameters
    dt = params["dt"]
    staking_mode = params["staking_mode"]
    Adoption_speed = params["Adoption_speed"]
    polygn_staked_process = params["polygn_staked_process"]

    # State Variables
    run = previous_state["run"]
    timestep = previous_state["timestep"]
    PRIVATE_CHAINS_CNT = previous_state["PRIVATE_CHAINS_CNT"]
    liveness_metrics = previous_state["liveness_metrics"]
    staking_metrics = previous_state["staking_metrics"]
    chain_specific_checkpoint_submission_cadence = previous_state["chain_specific_checkpoint_submission_cadence"]
    number_of_active_validators = previous_state["number_of_active_validators"]
    polygn_staked_per_validator = previous_state["polygn_staked_per_validator"]
    share_by_validator_in_SingleStaking = previous_state["share_by_validator_in_SingleStaking"]

    Adoption_speed = int(Adoption_speed / constants.epochs_per_month * dt)

    if polygn_staked_process(0, 0) is not None:
        polygn_staked = polygn_staked_process(run, timestep * dt)
        polygn_staked_per_validator *= polygn_staked
    
    chain_specific_checkpoint_submission_cadence = np.concatenate(
        (chain_specific_checkpoint_submission_cadence, np.random.binomial(1,0.5,Adoption_speed)+1), 
        axis=0)
    liveness_metrics = np.concatenate(
            (liveness_metrics, np.ones((Adoption_speed, number_of_active_validators), dtype=int)), 
            axis=0)

    if staking_mode == "MultiStaking":   
        staking_metrics = np.concatenate(( staking_metrics, np.repeat([list(polygn_staked_per_validator)], Adoption_speed, axis=0)), axis=0)
    elif staking_mode == "SingleStaking":
        share_by_new_validator_in_SingleStaking = np.reshape(
            np.random.poisson(5, Adoption_speed*number_of_active_validators),
            (Adoption_speed, number_of_active_validators)
        )
        share_by_validator_in_SingleStaking = np.concatenate(
            (share_by_validator_in_SingleStaking, share_by_new_validator_in_SingleStaking),
            axis=0
        )
        allocation_by_validator = (
            share_by_validator_in_SingleStaking 
            / share_by_validator_in_SingleStaking.sum(axis=0)
        )
        staking_metrics = allocation_by_validator * polygn_staked_per_validator
    PRIVATE_CHAINS_CNT = PRIVATE_CHAINS_CNT + Adoption_speed

    return {
        "chain_specific_checkpoint_submission_cadence": chain_specific_checkpoint_submission_cadence,
        "liveness_metrics": liveness_metrics,
        "staking_metrics":  staking_metrics,
        "PRIVATE_CHAINS_CNT": PRIVATE_CHAINS_CNT,
        "share_by_validator_in_SingleStaking": share_by_validator_in_SingleStaking,
    }

    