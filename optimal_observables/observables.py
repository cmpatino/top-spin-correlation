import numpy as np


def boost_to_frame(p_particle, p_frame):
    b = -p_frame[:, :3] / p_frame[:, 3:]
    b2 = np.sum(b ** 2, axis=1, keepdims=True)
    gamma = 1 / np.sqrt(1 - b2)
    bp = np.sum(p_particle[:, :3] * b, axis=1, keepdims=True)
    gamma2 = np.clip((gamma - 1) / b2, a_min=0, a_max=None)

    space_coords = (
        p_particle[:, :3] + (gamma2 * bp * b) + (gamma * b * p_particle[:, 3:])
    )
    time_coord = gamma * (p_particle[:, 3:] + bp)
    p_particle_boosted = np.concatenate([space_coords, time_coord], axis=1)
    return p_particle_boosted


def boost_to_com(p1, p2):
    p_com = p1 + p2
    return boost_to_frame(p1, p_com), boost_to_frame(p2, p_com), p_com


def create_basis(top_p_com):
    k_hat = top_p_com[:, :3] / np.linalg.norm(top_p_com[:, :3], axis=-1, keepdims=True)
    p_hat = np.array([0, 0, 1]).reshape(1, -1)
    theta = np.arccos(np.sum(k_hat * p_hat, axis=-1, keepdims=True))

    n_hat = np.cross(p_hat, k_hat) / np.sin(theta)
    r_hat = (p_hat - (k_hat * np.cos(theta))) / np.sin(theta)
    sign_mask = np.sign(np.cos(theta))
    n_hat *= sign_mask
    r_hat *= sign_mask
    return k_hat, r_hat, n_hat


def calculate_cosine_obs(p_particle, k_hat, r_hat, n_hat):
    basis_change = np.linalg.inv(np.stack([k_hat, r_hat, n_hat], axis=-1))
    p_new_basis = np.matmul(basis_change, np.expand_dims(p_particle[:, :3], axis=-1))
    obs = (
        p_new_basis[:, :3] / np.linalg.norm(p_new_basis, axis=1, keepdims=True)
    ).squeeze(-1)
    cos_k = obs[:, 0:1]
    cos_r = obs[:, 1:2]
    cos_n = obs[:, 2:3]
    return cos_k, cos_r, cos_n


def get_matrix(p_l_t, p_l_tbar, p_top, p_tbar, only_cosine_terms=False):
    p_top_com, p_tbar_com, p_com = boost_to_com(p_top, p_tbar)
    k_hat, r_hat, n_hat = create_basis(p_top_com)

    p_l_t_frame = boost_to_frame(p_l_t, p_top)
    p_l_tbar_frame = boost_to_frame(p_l_tbar, p_tbar)

    cos_k1, cos_r1, cos_n1 = calculate_cosine_obs(p_l_t_frame, k_hat, r_hat, n_hat)
    cos_k2, cos_r2, cos_n2 = calculate_cosine_obs(p_l_tbar_frame, k_hat, r_hat, n_hat)

    obs_matrix = np.concatenate(
        [
            cos_k1,
            cos_k2,
            cos_r1,
            cos_r2,
            cos_n1,
            cos_n2,
            cos_k1 * cos_k2,
            cos_r1 * cos_r2,
            cos_n1 * cos_n2,
            (cos_r1 * cos_k2) + (cos_k1 * cos_r2),
            (cos_r1 * cos_k2) - (cos_k1 * cos_r2),
            (cos_n1 * cos_r2) + (cos_r1 * cos_n2),
            (cos_n1 * cos_r2) - (cos_r1 * cos_n2),
            (cos_n1 * cos_k2) + (cos_k1 * cos_n2),
            (cos_n1 * cos_k2) - (cos_k1 * cos_n2),
        ],
        axis=1,
    )
    if only_cosine_terms:
        return obs_matrix[:, :6]
    return obs_matrix
