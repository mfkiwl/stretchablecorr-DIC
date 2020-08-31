# Error estimation

1. RMS (relative error). method implemented in skimage  
--> corresponds to peak amplitude $max(A \otimes B)$

2.   Cramér–Rao Bound & Fisher information matrix (??)  
--> corresponds to peak curvature 


##maths

$$
\underset{\delta}{\text{argmin}} \int_x \left[ A(x) - B(x+\delta) \right]^2 \, dx
$$


Let's consider the theoritical case where image $B$ is a pure translation of image $A$ plus a white centered noise:

$$
B = A(x + \delta) + \eta
$$

where $\eta$ is a white noise $\eta \sim \mathcal{N}(\sigma, \, 0)$


$$
P(B|\delta) = \prod_{pixels}\; \mathtt{N}( A(x)-B(x+\delta), \, \sigma ) 
$$

where $\mathtt{N}$ is the centered normal distribution:

$$
\mathtt{N}(u, \, \sigma) = \frac{1}{\sigma \sqrt{2\pi}}\exp(-\frac{u^2}{2\sigma^2}  )
$$

thus

$$
-\log P(B|\delta) = \sum_{pixels}\; \log(\sigma  \sqrt{2\pi}) + \frac{(A-B_\delta)^2}{2 \sigma^2}
$$

$$
-\log P(B|\delta) =  N\log(\sigma  \sqrt{2\pi}) + \frac{1}{2\sigma^2}\sum_{pixels}\; A^2 + B_\delta^2 - 2\,A\cdot B_\delta
$$

if $A$ and $B$ are normed:

$$
-\log P(B|\delta) =  N\log(\sigma  \sqrt{2\pi}) + \frac{1}{\sigma^2}\sum_{pixels}\; 1 - A\cdot B_\delta
$$

$$
-\log P(B|\delta) =  N\log(\sigma  \sqrt{2\pi}) + \frac{N}{\sigma^2} - \frac{1}{\sigma^2}\sum_{pixels}\, A\cdot B_\delta
$$

---

$$
log\,P(B|\delta) = \frac{1}{\sigma^2} \int (A(x)-B(x+\delta))^2 \,dx
$$

$$
log\,P(B|\delta) = -\frac{2}{\sigma^2} \left[ 1-  \int A(x)\cdot B(x+\delta) \,dx  \right]
$$ 
if $A$ and $B$ are normed, i.e. $\int A^2 = 1$

$$
log\,P(B|\delta) = -\frac{2}{\sigma^2} \left[ 1-  A\otimes B  \right]
$$ 

> integration bounds are lost, thus the normalization... $\mathbb{1}\otimes \mathbb{1}$ is not constant but pyramidal... or images are periodic...

entropy:

$$
P \cdot log\,P(B|\delta) = \sum \frac{2}{\sigma^2} \left[ 1-  A\otimes B  \right] \cdot \exp(-\frac{2}{\sigma^2} \left[ 1-  A\otimes B  \right])
$$ 



## References

- Kybic, J. « Bootstrap Resampling for Image Registration Uncertainty Estimation Without Ground Truth ». IEEE Transactions on Image Processing 19, nᵒ 1 (janvier 2010): 64‑73. https://doi.org/10.1109/TIP.2009.2030955.

- I. S. Yetik and A. Nehorai, “Performance bounds on image registration,” IEEE Transactions on Signal Processing, vol. 54, no. 5, pp. 1737–1749, May 2006, doi: 10.1109/TSP.2006.870552.

- D. Robinson and P. Milanfar, “Fundamental Performance Limits in Image Registration,” IEEE Transactions on Image Processing, vol. 13, no. 9, pp. 1185–1199, Sep. 2004, doi: 10.1109/TIP.2004.832923.