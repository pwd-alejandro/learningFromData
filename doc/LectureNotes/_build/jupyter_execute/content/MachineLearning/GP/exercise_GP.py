#!/usr/bin/env python
# coding: utf-8

# # Exercise: Gaussian processes using `GPy`

# *Adapted from the Gaussian Process Summer School (written by Nicolas Durrande, Neil Lawrence and James Hensman)*

# The aim of this exercise is to illustrate the concepts of Gaussian processes. We will focus on three aspects of GPs: the kernel, the random sample paths and the GP regression model.
# 
# We will use the well known [GPy package](https://sheffieldml.github.io/GPy/) by the Sheffield ML group.
# 
# The current draft of the online documentation of GPy is available from [this page](http://gpy.readthedocs.org/en/latest/).

# ## Part 1 
# ### Import modules

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
from matplotlib import pyplot as plt
import GPy

# Not really needed, but nicer plots
import seaborn as sns
sns.set()
sns.set_context("talk")


# ### Getting started: The Covariance Function

# Let's start with defining an exponentiated quadratic covariance function (also known as squared exponential or rbf or Gaussian) in one dimension:

# In[2]:


d = 1          # input dimension
var = 1.       # variance
theta = 0.2    # lengthscale
k = GPy.kern.RBF(d, variance=var, lengthscale=theta)


# A summary of the kernel can be obtained using the command `print k`. 

# In[3]:


print(k)


# It is also possible to plot the kernel as a function of one of its inputs (whilst fixing the other) with `k.plot()`.

# In[4]:


fig, ax = plt.subplots(figsize=(8,6))
k.plot(ax=ax);


# ### Setting Covariance Function Parameters

# The value of the covariance function parameters can be accessed and modified using `k['.*var']` where the string in bracket is a regular expression matching the parameter name as it appears in `print(k)`. Let's use this to get an insight into the effect of the parameters on the shape of the covariance function. 
# 
# We'll now use to set the lengthscale of the covariance to different values, and then plot the resulting covariance using the `k.plot()` method.

# In[5]:


k = GPy.kern.RBF(d)     # By default, the parameters are set to 1.
theta = np.asarray([0.2,0.5,1.,2.,4.])

fig, ax = plt.subplots(figsize=(8,6))
for it, t in enumerate(theta):
    k.lengthscale=t
    k.plot(ax=ax,color=f"C{it}")
    plt.legend(theta,title='lengthscale')


# ### Exercise 1

# a) What is the effect of the lengthscale parameter on the covariance function?
# Exercise 1 a) answer



# b) Now change the code used above for plotting the covariances associated with the length scale to see the influence of the variance parameter. What is the effect of the the variance parameter on the covariance function?

# In[6]:


# Exercise 1 b) answer
# insert code here



# ### Covariance Functions in GPy

# Many covariance functions are already implemented in GPy. Instead of rbf, try constructing and plotting the following  covariance functions: `Exponential`, `Matern32`, `Matern52`, `Brownian`, `Linear`, `Bias`,
# `StdPeriodic`, `PeriodicExponential`, etc. Some of these covariance functions have more hyperparameters than just a variance and a lengthscale. Furthermore, not all kernels are stationary (i.e., they can’t all be written as $k ( x, y) = f ( x − y)$, see for example the Brownian
# covariance function). For plotting, it may be interesting to change the value of the fixed input:

# In[7]:


kb1 = GPy.kern.PeriodicExponential(input_dim=1, variance=1.0, lengthscale=1.0, period=6.28)
kb2 = GPy.kern.StdPeriodic(input_dim=1, variance=1.0, lengthscale=1.0, period=6.28)
inputs = np.array([2., 4.])

fig, ax = plt.subplots(figsize=(8,6))
for ix, x in enumerate(inputs):
    kb1.plot(x,plot_limits=[0,5],ax=ax,color=f"C{ix}")
    kb2.plot(x,plot_limits=[0,5],ax=ax,color=f"C{ix}",linestyle='--')


# ### Computing the Covariance Function given the Input Data, $\mathbf{X}$

# Let $\mathbf{X}$ be a $n$ × $d$ numpy array. Given a kernel $k$, the covariance matrix associated to
# $\mathbf{X}$ is obtained with `C = k.K(X,X)` . The positive semi-definiteness of $k$ ensures that `C`
# is a positive semi-definite (psd) matrix regardless of the initial points $\mathbf{X}$. This can be
# checked numerically by looking at the eigenvalues:

# In[8]:


k = GPy.kern.Matern52(input_dim=2)
X = np.random.rand(50,2)       # 50*2 matrix of iid standard Gaussians
C = k.K(X,X)
eigvals = np.linalg.eigvals(C)           # Computes the eigenvalues of a matrix

fig, ax = plt.subplots(figsize=(8,6))
ax.bar(np.arange(len(eigvals)), np.log(eigvals))
ax.set(ylabel='log(eig)',title='Eigenvalues of the Matern 5/2 Covariance');


# ### Question
# 
# * Check this property for some other kernel and for a different set of points
# 
# 
# 

# ### Combining Covariance Functions

# ### Exercise 2

# a) A matrix, $\mathbf{K}$, is positive semi-definite if the matrix inner product, $\mathbf{x}^\top \mathbf{K}\mathbf{x}$ is greater than or equal to zero regardless of the values in $\mathbf{x}$. Given this it should be easy to see that the sum of two positive semi-definite matrices is also positive semi-definite. In the context of Gaussian processes, this is the sum of two covariance functions. What does this mean from a modelling perspective? 
# Exercise 2 a) answer



# *Hint*: there are actually two related interpretations for this. Think about the properties of a Gaussian distribution, and where the sum of Gaussian variances arises.

# b) What about the element-wise product of two covariance functions? In other words if we define

# \begin{align*}
# k(\mathbf{x}, \mathbf{x}^\prime) = k_1(\mathbf{x}, \mathbf{x}^\prime) k_2(\mathbf{x}, \mathbf{x}^\prime)
# \end{align*}

# then is $k(\mathbf{x}, \mathbf{x}^\prime)$ a valid covariance function?
# Exercise 2 b) answer



# ### Combining Covariance Functions in GPy

# In GPy you can easily combine covariance functions you have created using the sum and product operators, `+` and `*`. So, for example, if we wish to combine an exponentiated quadratic covariance with a Matern 5/2 then we can write

# In[9]:


kern1 = GPy.kern.RBF(1, variance=1., lengthscale=2.)
kern2 = GPy.kern.Matern52(1, variance=2., lengthscale=4.)
kern = kern1 + kern2
print(kern)
fig, ax = plt.subplots(figsize=(8,6))
kern.plot(ax=ax);


# Or if we wanted to multiply them we can write

# In[10]:


kern = kern1*kern2
print(kern)
fig, ax = plt.subplots(figsize=(8,6))
kern.plot(ax=ax);


# ## Part 2 
# ### Sampling from a Gaussian Process

# The Gaussian process provides a prior over an infinite dimensional function. It is defined by a covariance *function* and a mean *function*. When we compute the covariance matrix using `kern.K(X, X)` we are computing a covariance *matrix* between the values of the function that correspond to the input locations in the matrix `X`. If we want to have a look at the type of functions that arise from a particular Gaussian process we can never generate all values of the function, because there are infinite values. However, we can generate samples from a Gaussian *distribution* based on a covariance matrix associated with a particular matrix of input locations `X`. If these locations are chosen appropriately then they give us a good idea of the underlying function. For example, for a one dimensional function, if we choose `X` to be uniformly spaced across part of the real line, and the spacing is small enough, we'll get an idea of the underlying function. We will now use this trick to draw sample paths from a Gaussian process. 

# In[11]:


k = GPy.kern.RBF(input_dim=1,lengthscale=0.2)

X = np.linspace(0.,1.,500) # define X to be 500 points evenly spaced over [0,1]
X = X[:,None] # reshape X to make it n*p --- GPy uses 'design matrices'

mu = np.zeros(len(X)) # vector of the means --- we could use a mean function here, but here it is just zero.
C = k.K(X,X) # compute the covariance matrix associated with inputs X

# Generate 'nsamples' separate samples paths from a Gaussian with mean mu and covariance C
nsamples=10
Z = np.random.multivariate_normal(mu,C,nsamples)

fig, ax = plt.subplots(figsize=(8,6))
for i in range(nsamples):
    ax.plot(X[:],Z[i,:]);


# Our choice of `X` means that the points are close enough together to look like functions. We can see the structure of the covariance matrix we are plotting from if we visualize C.

# In[12]:


fig, ax = plt.subplots(figsize=(8,8))
ax.matshow(C);


# Now try a range of different covariance functions and values and plot the corresponding sample paths for each using the same approach given above.

# ### Exercise 3

# Modify the code below so that it plots the sampled paths from the nine different covariance structures that are generated. 

# In[13]:


figure, axes = plt.subplots(3,3, figsize=(12,12), tight_layout=True)
kerns = [GPy.kern.RBF(1), GPy.kern.Exponential(1), GPy.kern.Matern32(1), GPy.kern.Matern52(1), GPy.kern.Brownian(1), GPy.kern.Bias(1), GPy.kern.Linear(1), GPy.kern.PeriodicExponential(1), GPy.kern.White(1)]


X = np.linspace(0.,1.,500) 
X = X[:,None] 
mu = np.zeros(len(X)) # vector of the means --- we could use a mean function here, but here it is just zero.
nsamples=10    
    
for k,a in zip(kerns, axes.flatten()):
    C = k.K(X,X) # compute the covariance matrix associated with inputs X
    Z = np.random.multivariate_normal(mu,C,nsamples)
    a.set_title(k.name.replace('_', ' '))


# In[14]:


# Enter code here
#


# ## Part 3 
# ### A Gaussian Process Regression Model

# We will now combine the Gaussian process prior with some data to form a GP regression model with GPy. We will generate data from the function $f ( x ) = − \cos(\pi x ) + \sin(4\pi x )$ over $[0, 1]$, adding some noise to give $y(x) = f(x) + \epsilon$, with the noise being Gaussian distributed, $\epsilon \sim \mathcal{N}(0, 0.01)$. 

# In[15]:


X = np.linspace(0.05,0.95,10)[:,None]
Y = -np.cos(np.pi*X) + np.sin(4*np.pi*X) + np.random.normal(loc=0.0, scale=0.1, size=(10,1)) 
fig, ax = plt.subplots(figsize=(8,6))
ax.plot(X,Y,'kx',mew=1.5);


# A GP regression model based on an exponentiated quadratic covariance function can be defined by first defining a covariance function, 

# In[16]:


k = GPy.kern.RBF(input_dim=1, variance=1., lengthscale=1.)


# And then combining it with the data to form a Gaussian process model,

# In[17]:


m = GPy.models.GPRegression(X,Y,k)


# Just as for the covariance function object, we can find out about the model using the command `print(m)`. 

# In[18]:


print(m)


# Note that by default the model includes some observation noise
# with variance 1. We can see the posterior mean prediction and visualize the marginal posterior variances using `m.plot()`.
# 
# **Note:** The `plot` command shows the mean of the GP model as well as the 95% confidence region.

# In[19]:


m.plot();


# The actual predictions of the model for a set of points `Xnew` can be computed using 
# ```python
# Ynew, Yvar = m.predict(Xnew)
# ```
# 
# Note that `Xnew` is an $m \times p$ array, where $m$ is the number of points that we want to predict and $p$ is the dimensionality of the parameter space.
# 
# We can also extract the predictive quantiles around the prediction at `Xnew`.
# ```python
# Ylo95, Yhi95 = m.predict_quantiles(Xnew)
# ```
# 

# In[20]:


Xnew = np.linspace(0.0,1.5,4)[:,None]
(Ymean,Yvar) = m.predict(Xnew)
# quantiles=(2.5, 97.5) are default
(Ylo95,Yhi95) = m.predict_quantiles(Xnew)

print(r"  X   mean Y   var Y   lo95%   hi95%")
for (Xi,Ymeani,Yvari,Yloi,Yhii) in zip(Xnew,Ymean,Yvar,Ylo95,Yhi95):
    print(f"{Xi[0]:5.2f}  {Ymeani[0]:5.2f}   {Yvari[0]:5.2f}   {Yloi[0]:5.2f}   {Yhii[0]:5.2f}")


# ### Exercise 4

# a) What do you think about this first fit? Does the prior given by the GP seem to be
# adapted?
# Exercise 4 a) answer



# b) The parameters of the models can be modified using a regular expression matching the parameters names (for example `m['Gaussian_noise.variance'] = 0.001` ). Change the values of the parameters to obtain a better fit.

# In[21]:


# Exercise 4 b) 
# make a plot for a better fit here



# In[22]:


# KEY
m['Gaussian_noise.variance'] = 0.01
m['rbf.lengthscale'] = 0.1
fig, ax = plt.subplots(figsize=(8,6))
m.plot(ax=ax);


# c) As in Section 2, random sample paths from the conditional GP can be obtained using
# `np.random.multivariate_normal(mu[:,0],C)` where the mean vector and covariance
# matrix `mu`, `C` are obtained through the predict function `mu, C = m.predict(Xp,full_cov=True)`. Obtain 20 samples from the posterior sample and plot them alongside the data below. Compare the random sample paths to the 95% confidence region that is shown with the `m.plot()` command.

# In[23]:


# Exercise 4 c) answer



# ### Covariance Function Parameter Estimation

# The kernel parameter values can be estimated by maximizing the *likelihood* of the observations. Since we don’t want one of the variances to become negative during the optimization, we can constrain all parameters to be positive before running the optimisation.

# In[24]:


m.constrain_positive()


# The warnings are because the parameters are already constrained by default, the software is warning us that they are being reconstrained.

# Now we can optimize the model using the `m.optimize()` method.

# In[25]:


m.optimize()
fig, ax = plt.subplots(figsize=(8,6))
m.plot(ax=ax)
print(m)


# The parameters obtained after optimisation can be compared with the values selected by hand above. As previously, you can modify the kernel used for building the model to investigate its influence on the model.

# In[ ]:




