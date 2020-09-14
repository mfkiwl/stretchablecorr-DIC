# ===========================
#  Phase image registration
# ===========================

import numpy as np
from scipy.fft import fftn, ifftn
from scipy.fft import fftshift, fftfreq
from scipy.signal.windows import blackman
from scipy.optimize import minimize
from numba import jit

nopython = False

@jit(nopython=nopython)
def custom_fftfreq(n):
    """Return the Discrete Fourier Transform sample frequencies.
    same as numpy's `fftfreq` function but working with JIT (numba)
    https://github.com/numpy/numpy/blob/92ebe1e9a6aeb47a881a1226b08218175776f9ea/numpy/fft/helper.py#L124-L170
    """
    val = 1.0 / n
    results = np.empty(n, dtype=np.int64)
    N = (n-1)//2 + 1
    p1 = np.arange(0, N, dtype=np.int64)
    results[:N] = p1
    p2 = np.arange(-(n//2), 0, dtype=np.int64)
    results[N:] = p2
    return results * val


@jit(nopython=nopython)
def dft_dot(A, yx):
    """2D Discrete Fourier Transform of `A` at position `xy`

    Parameters
    ----------
    A : 2D array
    yx : tuple of floats (y, x)

    Returns
    -------
    complex
        value DFT of `A` at position `xy`
    """
    im2pi = 1j * 2 * np.pi
    y, x = yx
    yky = np.exp(im2pi * y * custom_fftfreq(A.shape[0]))
    xkx = np.exp(im2pi * x * custom_fftfreq(A.shape[1]))

    a = np.dot(A, xkx)
    a = np.dot(a, yky)
    return a / A.size


@jit(nopython=nopython)
def grad_dft(data, yx):
    """2D Discrete Fourier Transform of `grad(TF(A))` at position `xy`

    Parameters
    ----------
    A : 2D array
    yx : tuple of floats (y, x)

    Returns
    -------
    (2, 1) array of complex numbers
        value `grad(TF(A))` at position xy
    """
    im2pi = 1j * 2 * np.pi
    y, x = yx
    kx = im2pi * custom_fftfreq(data.shape[1])
    ky = im2pi * custom_fftfreq(data.shape[0])

    exp_kx = np.exp(x * kx)
    exp_ky = np.exp(y * ky)

    gradx = np.dot(data, exp_kx * kx)
    gradx = np.dot(gradx, exp_ky)

    grady = np.dot(data.T, exp_ky * ky)
    grady = np.dot(grady, exp_kx)

    return np.array([grady, gradx]) / data.size



def phase_registration_optim(A, B, phase=False, verbose=False):
    """Find translation between images A and B
    as the argmax of the (phase) cross correlation
    use iterative optimization

    Parameters
    ----------
    A, B : 2D arrays
        source and targer images
    phase : bool, optional
        if True use only the phase angle, by default False
    verbose : bool, optional
        if true print debug information, by default False

    Returns
    -------
    (2, 1) nd-array
        displacement vector (u_y, u_x)   (note the order Y, X)
    tuple of floats
        error estimations
    """
    #A = (A - np.min(A) )/np.std(A)
    #B = (B - np.min(B) )/np.std(B)
    upsamplefactor = 1

    if phase:
        u = blackman(A.shape[0])
        v = blackman(A.shape[1])
        window = u[:, np.newaxis] * v[np.newaxis, :]
    else:
        window = 1

    a = fftn(A * window)
    b = fftn(B * window)

    ab = a * b.conj()
    if phase:
        ab = ab / np.abs(ab)

    phase_corr = ifftn(fftshift(ab),
                       s=upsamplefactor*np.array(ab.shape))
    phase_corr = np.abs(fftshift(phase_corr))

    dx_span = fftshift(fftfreq(phase_corr.shape[1])) * A.shape[1]
    dy_span = fftshift(fftfreq(phase_corr.shape[0])) * A.shape[0]

    # argmax
    argmax_idx = np.unravel_index(np.argmax(phase_corr), phase_corr.shape)
    argmax = dy_span[argmax_idx[0]], dx_span[argmax_idx[1]]

    def cost(xy, ab):
        return -np.abs(dft_dot(ab, xy))

    def jac(xy, ab):
        return -np.real(grad_dft(ab, xy))

    res = minimize(cost, argmax,
                   args=(ab, ),
                   method='BFGS',
                   tol=1e-3,
                   jac=jac)
    if verbose:
        print(res)

    # Error estimation
    # from Inv. Hessian :
    a_moins_b_2 = (np.mean(A) - np.mean(B))**2
    sigma2 = np.mean(A**2 + B**2) - a_moins_b_2 + 2*res.fun/A.size
    C_theta = np.trace(res.hess_inv) * sigma2

    # CRBD :
    #ux = np.diff(A, axis=1).flatten()
    #uy = np.diff(A, axis=0).flatten()
    #ux2 = np.dot(ux, ux)
    #uy2 = np.dot(uy, uy)
    #uxy2 = np.dot(ux, uy)**2
    #CRBD = sigma2 * (ux2 + uy2)/(ux2*uy2 - uxy2)
    return -res.x, (1, C_theta)


def output_cross_correlation(A, B, upsamplefactor=1, phase=True):
    """Output the cross correlation image (or phase)
    for verification and debug

    Parameters
    ----------
    A, B : 2D array
        source and target images
    upsamplefactor : int, optional
        use zero-padding to interpolated the CC on a finer grid, by default 1
    phase : bool, optional
        if True norm the CC by its amplitude, by default True

    Returns
    -------
    1D array
        shift X value
    1D array
        shift Y value
    2D array
        phase corr
    tuple
        argmax from the optimization
    """
    if phase:
        u = blackman(A.shape[0])
        v = blackman(A.shape[1])
        window = u[:, np.newaxis] * v[np.newaxis, :]
    else:
        window = 1

    a, b = fftn(A * window), fftn(B * window)
    ab = a * b.conj()
    if phase:
        ab = ab / np.abs(ab)
    phase_corr = ifftn(fftshift(ab),
                       s=upsamplefactor*np.array(ab.shape))
    phase_corr = np.abs(fftshift(phase_corr))

    dx_span = fftshift(fftfreq(phase_corr.shape[1])) * A.shape[1]
    dy_span = fftshift(fftfreq(phase_corr.shape[0])) * A.shape[0]

    # argmax
    argmax_idx = np.unravel_index(np.argmax(phase_corr), phase_corr.shape)
    argmax = dy_span[argmax_idx[0]], dx_span[argmax_idx[1]]

    def cost(xy, ab):
        return -np.abs(dft_dot(ab, xy))

    def jac(xy, ab):
        return -np.real(grad_dft(ab, xy))

    res = minimize(cost, argmax,
                   args=(ab, ),
                   method='BFGS',
                   tol=1e-3,
                   jac=jac)

    return -dx_span, -dy_span, phase_corr, res
