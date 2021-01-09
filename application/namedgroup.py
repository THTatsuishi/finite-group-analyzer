"""
名前の付けられた群の生成子
"""
import numpy

class NamedGroupGenerator(object):
    
    @staticmethod
    def S_n(n: int) -> 'list[numpy.ndarray]':
        """
        Class: symmetric group (対称群),

        Name: S(n),

        Order: n!,

        Generators: n-1,

        Matrix dim.: n.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        generators = []
        for i1 in range(n-1):
            gen = numpy.zeros((n,n),dtype=numpy.int)
            for i2 in range(n):
                if i2 == i1:
                    gen[i2,i2+1] = 1
                elif i2 == i1 + 1:
                    gen[i2,i2-1] = 1
                else:
                    gen[i2,i2] = 1
            generators.append(gen) 
        return generators    
    
    @staticmethod
    def D_n(n: int) -> 'list[numpy.ndarray]':
        """
        Class: dihedral group (二面体群),

        Name: D(n),

        Order: 2n,

        Generators: 2,

        Matrix dim.: 2.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.cos(2*numpy.pi/float(n))
        q = numpy.sin(2*numpy.pi/float(n))
        gen1 = numpy.array([[p,-q],
                            [q,p]])
        gen2 = numpy.array([[1,0],
                            [0,-1]])
        return [gen1,gen2]

    @staticmethod
    def Q_n(n: int) -> 'list[numpy.ndarray]':
        """
        Class: binary dihedral group (),

        Name: Q(n),

        Order: 2n,

        Generators: 2,

        Matrix dim.: 2.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        q = numpy.exp(-2*numpy.pi*1j / float(n))
        gen1 = numpy.array([[p,0],
                            [0,q]])
        gen2 = numpy.array([[0,1j],
                            [1j,0]])
        return [gen1,gen2]
    
    @staticmethod
    def QD_2n(n: int) -> 'list[numpy.ndarray]':
        """
        Class:  (),

        Name: QD(2n),

        Order: 2n,

        Generators: 2,

        Matrix dim.: 2.

        Parameters
        ----------
        n : int
            n = 2^k, (k = 1,2,...).

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        q = numpy.exp(-2*numpy.pi*1j / float(n)) * (-1)
        gen1 = numpy.array([[p,0],
                            [0,q]])
        gen2 = numpy.array([[0,1],
                            [1,0]])
        return [gen1,gen2]

    @staticmethod
    def Sigma_2n_2(n: int) -> 'list[numpy.ndarray]':
        """
        Class:  (),

        Name: Sigma(2n^2),

        Order: 2n^2,

        Generators: 3,

        Matrix dim.: 2.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        gen1 = numpy.array([[1,0],
                            [0,p]])
        gen2 = numpy.array([[p,0],
                            [0,1]])
        gen3 = numpy.array([[0,1],
                            [1,0]])
        return [gen1,gen2,gen3]
    
    @staticmethod
    def Delta_3n_2(n: int) -> 'list[numpy.ndarray]':
        """
        Class:  (),

        Name: Delta(3n^2),

        Order: 3n^2,

        Generators: 3,

        Matrix dim.: 3.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        q = numpy.exp(-2*numpy.pi*1j / float(n))
        gen1 = numpy.array([[0,1,0],
                            [0,0,1],
                            [1,0,0]])
        gen2 = numpy.array([[p,0,0],
                            [0,1,0],
                            [0,0,q]])
        gen3 = numpy.array([[q,0,0],
                            [0,p,0],
                            [0,0,1]]) 
        return [gen1,gen2,gen3]
    
    # 本を確認せよ
    # gen2 を手動で変更する必要有り
    # （今は n = 19 の場合の値） 
    # @staticmethod
    # def T_n(n: int) -> 'list[numpy.ndarray]':
    #     """
    #     Class:  (),

    #     Name: T(n),

    #     Order: 3n,

    #     Generators: 2,

    #     Matrix dim.: 3.

    #     Parameters
    #     ----------
    #     n : int
    #         n = 7,13,19,31,43,49,....

    #     Returns
    #     -------
    #     list:
    #         Generators of the group.

    #     """
    #     p = numpy.exp(2*numpy.pi*1j / float(n))
    #     gen1 = numpy.array([[0,1,0],
    #                         [0,0,1],
    #                         [1,0,0]])
    #     gen2 = numpy.array([[p,0,0],
    #                         [0,p**7,0],
    #                         [0,0,p**11]])
    #     return [gen1,gen2]

    @staticmethod
    def Sigma_3n_3(n: int) -> 'list[numpy.ndarray]':
        """
        Class:  (),

        Name: Sgima(3n^3),

        Order: 3n^3,

        Generators: 4,

        Matrix dim.: 3.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        gen1 = numpy.array([[0,1,0],
                            [0,0,1],
                            [1,0,0]])
        gen2 = numpy.array([[1,0,0],
                            [0,1,0],
                            [0,0,p]])
        gen3 = numpy.array([[1,0,0],
                            [0,p,0],
                            [0,0,1]])
        gen4 = numpy.array([[p,0,0],
                            [0,1,0],
                            [0,0,1]])
        return [gen1,gen2,gen3,gen4]

    @staticmethod
    def Delta_6n_2(n: int) -> 'list[numpy.ndarray]':
        """
        Class:  (),

        Name: Delta(6n^2),

        Order: 6n^2,

        Generators: 4,

        Matrix dim.: 3.

        Parameters
        ----------
        n : int
            n > 0.

        Returns
        -------
        list:
            Generators of the group.

        """
        p = numpy.exp(2*numpy.pi*1j / float(n))
        q = numpy.exp(-2*numpy.pi*1j / float(n))
        gen1 = numpy.array([[0,1,0],
                            [0,0,1],
                            [1,0,0]])
        gen2 = numpy.array([[0,0,1],
                            [0,1,0],
                            [1,0,0]])
        gen3 = numpy.array([[p,0,0],
                            [0,q,0],
                            [0,0,1]])
        gen4 = numpy.array([[1,0,0],
                            [0,p,0],
                            [0,0,q]])
        return [gen1,gen2,gen3,gen4]