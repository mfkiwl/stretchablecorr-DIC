# Scipy 2D interpolation methods

https://docs.scipy.org/doc/scipy/reference/interpolate.html#multivariate-interpolation

## Unstructured data points

usually the points are meshed using Delaunay triangulation

- **`griddata`** : interface to different methods
    * NearestNDInterpolator
    * LinearNDInterpolator
    * CloughTocher2DInterpolator

- **`Rbf`** : radial basis function interpolation

- **`interp2d`** : Interpolate over a 2-D grid
    * uses `fitpack.bisplev`
    > line 228 : # TODO: surfit is really not meant for interpolation!

    * indeed, for unstructured data it is more a fit than an interpolation, as the spline knots do not correpond to entry data points

## Structured data points

- **`interpn`** : interface to different methods
    * RegularGridInterpolator
    * RectBivariateSpline

- **`RegularGridInterpolator`** :  
    * works on rectangular grid:
    
        pointstuple of ndarray of float, with shapes (m1, ), …, (mn, )

    * Python code
    * no derivative option for the call function

- **`RectBivariateSpline`** : 
    * subclass of BivariateSpline, which call _dfitpack_
    * works on rectangular grid (x,y 1-D arrays of coordinates)
    * derivative option for the call function


- **`bisplrep`** : (older wrapping) Low-level interface to FITPACK functions


so there is no quad-mesh 2D interpolation method !?  (for instance bilinear interpolation)

For instance [matplotlib's pcolormesh](https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.pcolormesh.html) works on a "non-regular rectangular grid"


## ndimage

- **`scipy.ndimage.map_coordinates`**
    * The order of the spline interpolation, default is 3. The order has to be in the range 0-5.
    * call `geometric_transform`, which call... [`NI_GeometricTransform`](https://github.com/scipy/scipy/blob/be591d5472f69dc47d971d1c69c73ae164034808/scipy/ndimage/src/ni_interpolation.c#L231) (ni_interpolation.c)


## Fortran FITPACK

the one used by Scipy is DIERCKX (see [code](https://github.com/scipy/scipy/tree/v1.5.2/scipy/interpolate/fitpack))

http://www.netlib.org/dierckx/

> DIERCKX is a package of Fortran subroutines for calculating smoothing splines for various kinds of data and geometries, with automatic knot selection. This library is also called FITPACK, but is independent of the FITPACK library by Alan Cline. 

> - ddierckx is a 'real*8' version of dierckx 
>    generated by Pearu Peterson <pearu@ioc.ee>.
> - dierckx (in netlib) is fitpack by P. Dierckx