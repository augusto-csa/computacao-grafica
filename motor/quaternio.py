import numpy as np
import math

# Classe para criacao e manipulacao de quaternios, essenciais para rotacoes 3D
# Eles evitam problemas como o "Gimbal Lock" e permitem interpolacoes muito mais suaves
class QuaternioCalc:
    def __init__(self, real, i, j, k):
        # Inicializa o quaternio com sua parte real (r) e suas partes imaginarias (i, j, k)
        self.r, self.i, self.j, self.k = real, i, j, k

    def normalizar(self):
        # Calcula a magnitude (tamanho) do quaternio usando o Teorema de Pitagoras em 4D
        mag = math.sqrt(self.r**2 + self.i**2 + self.j**2 + self.k**2)
        
        # Se a magnitude nao for zero, divide todas as componentes por ela
        # Isso garante que o quaternio se torne "unitario" (tamanho igual a 1)
        if mag != 0:
            self.r /= mag; self.i /= mag; self.j /= mag; self.k /= mag
        return self

    @staticmethod
    def criar_de_eixo_angulo(eixo, angulo_rad):
        # Metodo estatico que cria um quaternio a partir de um eixo de rotacao (vetor 3D) e um angulo
        vetor = np.array(eixo, dtype=float)
        
        # Calcula o tamanho do vetor do eixo
        norma = np.linalg.norm(vetor)
        
        # Se o vetor for nulo, retorna o quaternio identidade (sem rotacao)
        if norma == 0: return QuaternioCalc(1, 0, 0, 0)
        
        # Transforma o eixo em um vetor unitario
        vetor_unitario = vetor / norma
        
        # A formula matematica do quaternio sempre utiliza a metade do angulo
        metade_ang = angulo_rad / 2.0
        s = math.sin(metade_ang)
        
        # Retorna o quaternio: r recebe o cosseno, e as partes imaginarias recebem o eixo multiplicado pelo seno
        return QuaternioCalc(math.cos(metade_ang), vetor_unitario[0]*s, vetor_unitario[1]*s, vetor_unitario[2]*s)

    def para_matriz4x4(self):
        # Converte o quaternio atual para uma matriz homogenea de rotacao 4x4 (padrao em computacao grafica)
        
        # Sempre normaliza antes de converter para evitar distorcoes de escala no objeto
        self.normalizar()
        r, i, j, k = self.r, self.i, self.j, self.k
        
        # Matriz resultante baseada na multiplicacao algebrica das componentes do quaternio unitario
        return np.array([
            [1 - 2*(j**2 + k**2), 2*(i*j - r*k),       2*(i*k + r*j),       0],
            [2*(i*j + r*k),       1 - 2*(i**2 + k**2), 2*(j*k - r*i),       0],
            [2*(i*k - r*j),       2*(j*k + r*i),       1 - 2*(i**2 + j**2), 0],
            [0,                   0,                   0,                   1]
        ])

    @staticmethod
    def interpolacao_esferica(qa, qb, fator_t):
        # SLERP (Spherical Linear Interpolation)
        # Calcula uma rotacao suave intermediaria entre dois quaternios (qa e qb) baseada num fator de tempo 't' (0.0 a 1.0)
        
        # Garante que ambos sejam unitarios para percorrerem a superficie de uma esfera perfeita
        qa.normalizar(); qb.normalizar()
        
        # Produto escalar (dot product) descobre a diferenca de angulo entre as duas rotacoes
        dot = qa.r*qb.r + qa.i*qb.i + qa.j*qb.j + qa.k*qb.k
        
        # Se o produto escalar for negativo, inverte um quaternio para pegar o caminho mais curto na esfera
        if dot < 0.0:
            qb = QuaternioCalc(-qb.r, -qb.i, -qb.j, -qb.k)
            dot = -dot
            
        # Se os dois quaternios forem quase identicos, usa interpolacao linear simples (LERP) para evitar divisao por zero
        if dot > 0.9995:
            return QuaternioCalc(qa.r + fator_t*(qb.r - qa.r), qa.i + fator_t*(qb.i - qa.i), qa.j + fator_t*(qb.j - qa.j), qa.k + fator_t*(qb.k - qa.k)).normalizar()

        # Calcula o angulo total entre as duas rotacoes
        theta_0 = math.acos(dot)
        # Calcula o angulo parcial equivalente ao momento atual 't' da animacao
        theta_t = theta_0 * fator_t
        
        # Calcula os senos necessarios para definir os pesos geometricos
        seno_0 = math.sin(theta_0)
        seno_t = math.sin(theta_t)

        # Calcula o peso (influencia) do quaternio inicial (qa)
        peso_a = math.cos(theta_t) - dot * seno_t / seno_0
        # Calcula o peso (influencia) do quaternio final (qb)
        peso_b = seno_t / seno_0
        
        # Mistura os valores com base nos pesos e retorna o quaternio resultante exato
        return QuaternioCalc(peso_a*qa.r + peso_b*qb.r, peso_a*qa.i + peso_b*qb.i, peso_a*qa.j + peso_b*qb.j, peso_a*qa.k + peso_b*qb.k)