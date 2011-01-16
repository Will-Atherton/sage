r"""
Library of cythonized methods
"""

#*****************************************************************************
#       Copyright (C) 2010 Harald Schilly <harald.schilly@gmail.com>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.misc import prod

include '../ext/interrupt.pxi'
include '../ext/cdefs.pxi'
include "../ext/stdsage.pxi"

cpdef julia(ff_j, z, int iterations):
    """
    Helper function for the Julia Fractal interact example.

    INPUT:

        - `ff_j` -- fast callable for the inner iteration
        - `z` -- complex number
        - `iterations` -- number of loops

    TESTS::

        sage: from sage.interacts.library_cython import julia
        sage: z = var('z')
        sage: c_real, c_imag = 1, 1
        sage: f = symbolic_expression(z**2 + c_real + c_imag * CDF.gen()).function(z)
        sage: ff_m = fast_callable(f, vars=[z], domain=CDF)
        sage: julia(ff_m, CDF(1,1), 3)
        1.0 + 3.0*I
    """
    for i in range(iterations):
         z = ff_j(z)
         if z.abs() > 2: break
    return z

cpdef mandel(ff_m, z, int iterations):
    """
    Helper function for the Mandelbrot Fractal interact example.

    INPUT:

        - `ff_m` -- fast callable for the inner iteration
        - `z` -- complex number
        - `iterations` -- number of loops

    TESTS::

        sage: from sage.interacts.library_cython import mandel
        sage: z, c = var('z, c')
        sage: f = symbolic_expression(z**2 + c).function(z,c)
        sage: ff_m = fast_callable(f, vars=[z,c], domain=CDF)
        sage: mandel(ff_m, CDF(1,1), 3)
        1.0 + 3.0*I

    """
    c = z
    for i in range(iterations):
        z = ff_m(z, c)
        if z.abs() > 2: break
    return z


cpdef cellular(rule, int N):
    '''
    Cythonized helper function for the callular_automata fractal.
    Yields a matrix showing the evolution of a Wolfram's cellular automaton.
    Based on work by Pablo Angulo.
    http://wiki.sagemath.org/interact/misc#CellularAutomata

    INPUT:

        - `rule` -- determines how a cell's value is updated, depending on its neighbors
        - `N` -- number of iterations

    TESTS::

        sage: from sage.interacts.library_cython import cellular
        sage: rule = [1, 0, 1, 0, 0, 1, 1, 0]
        sage: N = 3
        sage: print cellular(rule, 3)

    '''
    from numpy import zeros
    cdef int j, k, l
    M=zeros((N, 2*N+1), dtype=int)
    M[0,N]=1

    for j in range(1, N):
        for k in range(N-j, N+j+1):
            l = 4 * M[j-1, k-1] + 2 * M[j-1, k] + M[j-1, k+1]
            M[j,k] = rule[l]
    return M
