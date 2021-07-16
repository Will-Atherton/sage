"""
Jacobian of a general hyperelliptic curve
"""

# ****************************************************************************
#  Copyright (C) 2006 David Kohel <kohel@maths.usyd.edu>
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
# ****************************************************************************

from sage.rings.all import Integer
from sage.misc.lazy_attribute import lazy_attribute
from sage.schemes.jacobians.abstract_jacobian import Jacobian_generic
from sage.schemes.generic.homset import SchemeHomset_generic
from . import jacobian_homset
from . import jacobian_morphism


class HyperellipticJacobian_generic(Jacobian_generic):
    """
    EXAMPLES::

        sage: FF = FiniteField(2003)
        sage: R.<x> = PolynomialRing(FF)
        sage: f = x**5 + 1184*x**3 + 1846*x**2 + 956*x + 560
        sage: C = HyperellipticCurve(f)
        sage: J = C.jacobian()
        sage: a = x**2 + 376*x + 245; b = 1015*x + 1368
        sage: X = J(FF)
        sage: D = X([a,b])
        sage: D
        (x^2 + 376*x + 245, y + 988*x + 635)
        sage: J(0)
        (1)
        sage: D == J([a,b])
        True
        sage: D == D + J(0)
        True

    An more extended example, demonstrating arithmetic in J(QQ) and
    J(K) for a number field K/QQ.

    ::

        sage: P.<x> = PolynomialRing(QQ)
        sage: f = x^5 - x + 1; h = x
        sage: C = HyperellipticCurve(f,h,'u,v')
        sage: C
        Hyperelliptic Curve over Rational Field defined by v^2 + u*v = u^5 - u + 1
        sage: PP = C.ambient_space()
        sage: PP
        Projective Space of dimension 2 over Rational Field
        sage: C.defining_polynomial()
        -x0^5 + x0*x1*x2^3 + x1^2*x2^3 + x0*x2^4 - x2^5
        sage: C(QQ)
        Set of rational points of Hyperelliptic Curve over Rational Field defined by v^2 + u*v = u^5 - u + 1
        sage: K.<t> = NumberField(x^2-2)
        sage: C(K)
        Set of rational points of Hyperelliptic Curve over Number Field in t with defining polynomial x^2 - 2 defined by v^2 + u*v = u^5 - u + 1
        sage: P = C(QQ)(0,1,1); P
        (0 : 1 : 1)
        sage: P == C(0,1,1)
        True
        sage: C(0,1,1).parent()
        Set of rational points of Hyperelliptic Curve over Rational Field defined by v^2 + u*v = u^5 - u + 1
        sage: P1 = C(K)(P)
        sage: P2 = C(K)([2,4*t-1,1])
        sage: P3 = C(K)([-1/2,1/8*(7*t+2),1])
        sage: P1, P2, P3
        ((0 : 1 : 1), (2 : 4*t - 1 : 1), (-1/2 : 7/8*t + 1/4 : 1))
        sage: J = C.jacobian()
        sage: J
        Jacobian of Hyperelliptic Curve over Rational Field defined by v^2 + u*v = u^5 - u + 1
        sage: Q = J(QQ)(P); Q
        (u, v - 1)
        sage: for i in range(6): Q*i
        (1)
        (u, v - 1)
        (u^2, v + u - 1)
        (u^2, v + 1)
        (u, v + 1)
        (1)
        sage: Q1 = J(K)(P1); print("%s -> %s"%( P1, Q1 ))
        (0 : 1 : 1) -> (u, v - 1)
        sage: Q2 = J(K)(P2); print("%s -> %s"%( P2, Q2 ))
        (2 : 4*t - 1 : 1) -> (u - 2, v - 4*t + 1)
        sage: Q3 = J(K)(P3); print("%s -> %s"%( P3, Q3 ))
        (-1/2 : 7/8*t + 1/4 : 1) -> (u + 1/2, v - 7/8*t - 1/4)
        sage: R.<x> = PolynomialRing(K)
        sage: Q4 = J(K)([x^2-t,R(1)])
        sage: for i in range(4): Q4*i
        (1)
        (u^2 - t, v - 1)
        (u^2 + (-3/4*t - 9/16)*u + 1/2*t + 1/4, v + (-1/32*t - 57/64)*u + 1/2*t + 9/16)
        (u^2 + (1352416/247009*t - 1636930/247009)*u - 1156544/247009*t + 1900544/247009, v + (-2326345442/122763473*t + 3233153137/122763473)*u + 2439343104/122763473*t - 3350862929/122763473)
        sage: R2 = Q2*5; R2
        (u^2 - 3789465233/116983808*u - 267915823/58491904, v + (-233827256513849/1789384327168*t + 1/2)*u - 15782925357447/894692163584*t)
        sage: R3 = Q3*5; R3
        (u^2 + 5663300808399913890623/14426454798950909645952*u - 26531814176395676231273/28852909597901819291904, v + (253155440321645614070860868199103/2450498420175733688903836378159104*t + 1/2)*u + 2427708505064902611513563431764311/4900996840351467377807672756318208*t)
        sage: R4 = Q4*5; R4
        (u^2 - 3789465233/116983808*u - 267915823/58491904, v + (233827256513849/1789384327168*t + 1/2)*u + 15782925357447/894692163584*t)

    Thus we find the following identity::

        sage: 5*Q2 + 5*Q4
        (1)

    Moreover the following relation holds in the 5-torsion subgroup::

        sage: Q2 + Q4 == 2*Q1
        True

    TESTS::

        sage: k.<a> = GF(9); R.<x> = k[]
        sage: J1 = HyperellipticCurve(x^3 + x - 1, x+a).jacobian()
        sage: FF = FiniteField(2003)
        sage: R.<x> = PolynomialRing(FF)
        sage: f = x**5 + 1184*x**3 + 1846*x**2 + 956*x + 560
        sage: J2 = HyperellipticCurve(f).jacobian()
        sage: J1 == J1
        True
        sage: J1 == J2
        False
    """
    def dimension(self):
        """
        Return the dimension of this Jacobian.

        OUTPUT:

        Integer

        EXAMPLES::

            sage: k.<a> = GF(9); R.<x> = k[]
            sage: HyperellipticCurve(x^3 + x - 1, x+a).jacobian().dimension()
            1
            sage: g = HyperellipticCurve(x^6 + x - 1, x+a).jacobian().dimension(); g
            2
            sage: type(g)
            <... 'sage.rings.integer.Integer'>
        """
        return Integer(self.curve().genus())

    def point(self, mumford, check=True):
        try:
            return self(self.base_ring())(mumford)
        except AttributeError:
            raise ValueError("Arguments must determine a valid Mumford divisor.")

    def _point_homset(self, *args, **kwds):
        return jacobian_homset.JacobianHomset_divisor_classes(*args, **kwds)

    def _point(self, *args, **kwds):
        return jacobian_morphism.JacobianMorphism_divisor_class_field(*args, **kwds)

    ####################################################################
    # Endomorphism rings and related properties
    ####################################################################

    @lazy_attribute
    def __endomorphism_ring(self):
        """
        Private constructor of endomorphism ring. It is expected that the
        user would simply call `endomorphism_ring()`.

        EXAMPLES::

            sage: R.<x> = QQ[]
            sage: f = x^6 + 4*x^5 + 6*x^4 + 2*x^3 + x^2 + 2*x + 1
            sage: C = HyperellipticCurve(f)
            sage: J = C.jacobian()
            sage: E = J.__endomorphism_ring
            sage: E
            Endomorphism ring of Jacobian of Hyperelliptic Curve over Rational Field defined by y^2 = x^6 + 4*x^5 + 6*x^4 + 2*x^3 + x^2 + 2*x + 1
        """
        from .jacobian_endomorphisms import EndomorphismRing
        return EndomorphismRing(self)

    def endomorphism_ring(self):
        """
        The ring of endomorphisms of this Jacobian which are defined over
        the base field.

        EXAMPLES::

            sage: R.<x> = QQ[]
            sage: f = x^6 + 78*x^5 + 16*x^2 + x + 8
            sage: C = HyperellipticCurve(f)
            sage: J = C.jacobian()
            sage: E = J.endomorphism_ring()
            sage: E
            Endomorphism ring of Jacobian of Hyperelliptic Curve over Rational Field defined by y^2 = x^6 + 78*x^5 + 16*x^2 + x + 8
        """
        return self.__endomorphism_ring

    def is_generic(self, B=200, proof=False):
        r"""
        Returns whether the geometric endomorphism algebra of ``self`` is the
        integer ring `\ZZ`.

        INPUT:

        - ``B`` -- (default: 200) the bound which appears in the statement of
          the algorithm from [Lom2019]_

        - ``proof`` -- (default: False) whether or not to insist on a provably
        correct answer. This is related to the warning in the module docstring
        of `jacobian_endomorphisms.py`: if this function returns `False`, then
        strictly speaking this has not been proven to be `False` until one has
        exhibited a non-trivial endomorphism, which the methods in that module
        are not designed to carry out. If one is convinced that this method
        should return `True`, but it is returning `False`, then this can be
        exhibited by increasing `B`.

        OUTPUT:

            Boolean indicating whether or not the geometric endomorphism
            ring is isomorphic to the integer ring.

        EXAMPLES:

        This is LMFDB curve 603.a.603.2::

            sage: R.<x> = QQ[]
            sage: f = 4*x^5 + x^4 - 4*x^3 + 2*x^2 + 4*x + 1
            sage: C = HyperellipticCurve(f)
            sage: J = C.jacobian()
            sage: E = J.endomorphism_ring()
            sage: E.is_geometrically_trivial()
            True

        This is LMFDB curve 1152.a.147456.1 whose geometric endomorphism ring
        is isomorphic to the group of 2x2 matrices over `\QQ`::

            sage: f = x^6 - 2*x^4 + 2*x^2 - 1
            sage: C = HyperellipticCurve(f)
            sage: J = C.jacobian()
            sage: E = J.endomorphism_ring()
            sage: E.is_geometrically_trivial()
            False

        This is LMFDB curve 20736.k.373248.1 whose geometric endomorphism ring
        is isomorphic to the group of 2x2 matrices over a CM field::

            sage: f = x^6 + 8
            sage: C = HyperellipticCurve(f)
            sage: J = C.jacobian()
            sage: E = J.endomorphism_ring()
            sage: E.is_geometrically_trivial()
            False
        """
        return self.endomorphism_ring().is_geometrically_trivial(B=B)
