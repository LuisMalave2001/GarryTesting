# -*- coding: utf-8 -*-

import math

class NumberToTextConverter:


    def __init__(self, moneda_singular, moneda_plural, centavo_singular, centavo_plural):
        self.moneda_singular = moneda_singular
        self.moneda_plural = moneda_plural

        self.centavo_singular = centavo_singular
        self.centavo_plural = centavo_plural

    def _unidades(self, num):
        unidades = {
            1: "UN",
            2: "DOS",
            3: "TRES",
            4: "CUATRO",
            5: "CINCO",
            6: "SEIS",
            7: "SIETE",
            8: "OCHO",
            9: "NUEVE",
        }
        return unidades.get(num, "")
    
    def _decenas(self, num):

        decena = math.floor(num / 10)
        unidad = num - (decena * 10)

        numero = ""

        if decena == 1:
            numero = {
                0: "DIEZ",
                1: "ONCE",
                2: "DOCE",
                3: "TRECE",
                4: "CATORCE",
                5: "QUINCE",
            }.get(unidad, "DIECI" + self._unidades(unidad))
        elif decena == 2:
            numero = {
                0: "VEINTE"
            }.get(unidad, "VEINTI" + self._unidades(unidad))
        else:
            if decena > 0:
                decena_str = {
                    3: "TREINTA",
                    4: "CUARENTA",
                    5: "CINCUENTA",
                    6: "SESENTA",
                    7: "SETENTA",
                    8: "OCHENTA",
                    9: "NOVENTA",
                }.get(decena, "UNKNOWN")
                numero = decena_str
                if unidad > 0:
                    numero += " Y %s" % self._unidades(unidad)
            else:
                numero = self._unidades(unidad)

        return numero
    
    def _centenas(self, num):
        centena = math.floor(num / 100)
        decena = num - (centena * 100)

        numero = ""

        if centena == 1:
            if decena > 0:
                numero = "CIENTO %s" % self._decenas(decena) 
            else:
                numero = "CIEN"
        elif centena > 1:
            centena_str = {
                2: "DOSCIENTOS",
                3: "TRECIENTOS",
                4: "CUATROCIENTOS",
                5: "QUINIENTOS",
                6: "SEISCIENTOS",
                7: "SETECIENTOS",
                8: "OCHOCIENTOS",
                9: "NOVECIENTOS",
            }.get(centena, "UNKNOWN")

            numero = "%s %s" % (centena_str, self._decenas(decena))
        else:
            numero = self._decenas(decena)

        return numero

    def _seccion(self, num, divisor, singular, plural):
        cientos = math.floor(num / divisor)
        numero = ""

        if cientos > 0:
            if cientos > 1:
                numero = self._centenas(cientos) + " " + plural
            else:
                numero = singular

        return numero
    

    def _miles(self, num):
        divisor = 1000
        cientos = math.floor(num / divisor)
        resto = num - (cientos * divisor)

        miles = self._seccion(num, divisor, "UN MIL", "MIL")
        centena = self._centenas(resto)

        if not miles:
            return centena
        
        return "%s %s" % (miles, centena)


    def _millones(self, num):
        divisor = 1000000
        cientos = math.floor(num / divisor)
        resto = num - (cientos * divisor)

        miles = self._seccion(num, divisor, "UN MILLLÓN", "MILLONES")
        centena = self._miles(resto)

        if not miles:
            return centena
        
        numero = "%s %s" % (miles, centena)

        return numero.strip()
        
    def numero_a_letra(self, num):
        data = {
            "numero": num,
            "enteros": math.floor(num),
            "centavos": (((round(num * 100)) - (math.floor(num) * 100))),
            "letrasCentavos": "",
            "letrasMonedaPlural": self.moneda_plural, #"PESOS", 'Dólares', 'Bolívares', 'etcs'
            "letrasMonedaSingular": self.moneda_singular, #"PESO", 'Dólar', 'Bolivar', 'etc'

            "letrasMonedaCentavoPlural": self.centavo_plural,
            "letrasMonedaCentavoSingular": self.centavo_singular,
        }

        if data["centavos"] > 0:
            data["letrasCentavos"] = " CON " + (self._millones(data["centavos"]) + " " + data["letrasMonedaCentavoSingular"] \
                                                if data["centavos"] == 1 else self._millones(data["centavos"]) + " " + data["letrasMonedaCentavoPlural"]) 

        if data["enteros"] == 0:
            return "CERO " + data["letrasMonedaPlural"] + "" + data["letrasCentavos"]
        if data["enteros"] == 1:
            return self._millones(data["enteros"]) + " " + data["letrasMonedaSingular"] + "" + data["letrasCentavos"]
        else:
            return self._millones(data["enteros"]) + " " + data["letrasMonedaPlural"] + "" + data["letrasCentavos"]


# Testing
if __name__ == "__main__":
    converter = NumberToTextConverter("LP.", "LPS.", "CTV.", "CTVS.")
    for i in range(0, 1000000000):
        print("%i %s" % (i, converter.numero_a_letra(i)))