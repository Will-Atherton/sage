r"""
Modular Forms for `\Gamma_0(N)` over `\QQ`

TESTS::

    sage: m = ModularForms(Gamma0(389),6)
    sage: loads(dumps(m)) == m
    True
"""

#########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#########################################################################

import sage.rings.all as rings

import sage.modular.arithgroup.all as arithgroup

import ambient
import cuspidal_submodule
import eisenstein_submodule
import submodule

class ModularFormsAmbient_g0_Q(ambient.ModularFormsAmbient):
    """
    A space of modular forms for `\Gamma_0(N)` over `\QQ`.
    """
    def __init__(self, level, weight):
        r"""
        Create a space of modular symbols for `\Gamma_0(N)` of given
        weight defined over `\QQ`.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(11),4); m
            Modular Forms space of dimension 4 for Congruence Subgroup Gamma0(11) of weight 4 over Rational Field
            sage: type(m)
            <class 'sage.modular.modform.ambient_g0.ModularFormsAmbient_g0_Q'>
        """
        ambient.ModularFormsAmbient.__init__(self, arithgroup.Gamma0(level), weight, rings.QQ)

    ####################################################################
    # Computation of Special Submodules
    ####################################################################
    def cuspidal_submodule(self):
        r"""
        Return the cuspidal submodule of this space of modular forms for
        `\Gamma_0(N)`.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(33),4)
            sage: s = m.cuspidal_submodule(); s
            Cuspidal subspace of dimension 10 of Modular Forms space of dimension 14 for Congruence Subgroup Gamma0(33) of weight 4 over Rational Field
            sage: type(s)
            <class 'sage.modular.modform.cuspidal_submodule.CuspidalSubmodule_g0_Q'>
        """
        try:
            return self.__cuspidal_submodule
        except AttributeError:
            if self.level() == 1:
                self.__cuspidal_submodule = cuspidal_submodule.CuspidalSubmodule_level1_Q(self)
            else:
                self.__cuspidal_submodule = cuspidal_submodule.CuspidalSubmodule_g0_Q(self)
        return self.__cuspidal_submodule

    def eisenstein_submodule(self):
        r"""
        Return the Eisenstein submodule of this space of modular forms for
        `\Gamma_0(N)`.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(389),6)
            sage: m.eisenstein_submodule()
            Eisenstein subspace of dimension 2 of Modular Forms space of dimension 163 for Congruence Subgroup Gamma0(389) of weight 6 over Rational Field
        """
        try:
            return self.__eisenstein_submodule
        except AttributeError:
            self.__eisenstein_submodule = eisenstein_submodule.EisensteinSubmodule_g0_Q(self)
        return self.__eisenstein_submodule

    def _compute_atkin_lehner_matrix(self, d):
        r"""
        Compute the matrix of the Atkin-Lehner involution W_d acting on self,
        where d is a divisor of the level.  This is only implemented in the
        (trivial) level 1 case.

        EXAMPLE::

            sage: ModularForms(1, 30).atkin_lehner_operator()
            Hecke module morphism Atkin-Lehner operator W_1 defined by the matrix
            [1 0 0]
            [0 1 0]
            [0 0 1]
            Domain: Modular Forms space of dimension 3 for Modular Group SL(2,Z) ...
            Codomain: Modular Forms space of dimension 3 for Modular Group SL(2,Z) ...
        """
        if self.level() == 1:
            from sage.matrix.matrix_space import MatrixSpace
            return MatrixSpace(self.base_ring(), self.rank())(1)
        else:
            raise NotImplementedError
