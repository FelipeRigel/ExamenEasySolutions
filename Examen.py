import psycopg2
import random
from datetime import datetime

def connect():
	try:
		conn = psycopg2.connect("dbname='ExamenDB' user='postgres' host='localhost' password='a' port=5432")
	except:
		print "I am unable to connect to the database"
	return conn

#---------------------------------[Funciones de la base de datos]------------------------------

#Ejecutador de las queries
def DB_execute(commands,insert=False,select=False):
	c=""
	try:
		# connect to the PostgreSQL server
		conn = connect()
		cur = conn.cursor()
		# execute Queries one by one
		
		if insert:
			cur.execute(commands[0],commands[1])
			conn.commit()

		elif select:
			cur.execute(commands)
			c=cur.fetchall()
			

		else: 
			for command in commands:
				cur.execute(command)
		
		# close communication with the PostgreSQL database server
		cur.close()
		# commit the changes
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
			conn.close()
			print "Done"

	return c

#Creador de tableas
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE Report (
                report_id SERIAL PRIMARY KEY,
                report_val_result BOOLEAN NOT NULL,
                report_text_result VARCHAR NOT NULL,
                date_run	DATE
        )
        """,
        """
        CREATE TABLE Proof_Standar (
                proof_id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                positive_outcome VARCHAR NOT NULL,
                negative_outcome VARCHAR NOT NUlL
        )
        """
        )
    DB_execute(commands)

#Rellena los datos que ya venian identificados en el reporte
def insertDefaultData():
	""" insert the Default Data in the PostgreSQL database"""
	commands = (
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Nivel de aceite','Por arriba de los normal','por debajo de lo normal');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Nivel de anticongelante','Por arriba de los normal','por debajo de lo normal');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Presion de neumaticos','Correctamente inflada','Sobre inflada;Desinflada');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Sistema electrico','Corretamente funcionando','Falla electrica');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Bateria','Buen estado','Estado regular;Mal estado');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Sistema A/C','Correctamente Funcionando','Falla Tecnica');
	    """,
	    """
	    INSERT INTO Proof_Standar (proof_id,name,positive_outcome,negative_outcome) VALUES
	    (DEFAULT,'Sistema frenado','Correctamente Funcionando','Falla Tecnica;Detalle Tecnico');
	    """
	    )
	    
	DB_execute(commands)

#---------------------------------[Clases]------------------------------

class Proof_Standar:
	def __init__(self,name,aprovedText,notaprovedText,testResult=False):

		self.name=name
		self.testResult=False
		#check if one string or list, and convert to list element
		self.aprovedText=aprovedText.split(";")
		self.notaprovedText=notaprovedText.split(";")
    
	def proofTest(self):
		print "Prueba: \""+self.name+"\""
		joinlist=self.aprovedText+self.notaprovedText
		choise = 0
		for option in joinlist: 
			choise=choise+1
			print "\t"+str(choise)+")"+option+"."
		ans=int(random.choice(range(len(joinlist)-1)))+1#raw_input("Elije el resultado de la prueba: ")
		while not(isinstance(ans,int)) or ans > len(joinlist)or ans<1:
			print ans 
			print "Seleccione una respuesta segun los numeros en las opciones..."
			ans=raw_input("Elije el resultado de la1 prueba: ")
		  
		if ans <= len(self.aprovedText):
		  self.testResult=True
		elif (ans<=len(joinlist)):
		  self.testResult=False
		return [self.testResult,joinlist[ans-1]]

class Report_class():
	def __init__(self,Proofs=[]):
		self.proofs=Proofs
		self.date= ""
		self.report_val_result = True
		self.text_result  =  ""
	def addProof(self,proof):
		self.proofs.append(proof)
	def runTest(self):
		for p in self.proofs:
			R=p.proofTest()
			if not R[0]:
				self.text_result=self.text_result+"\n"+R[1]
				self.report_val_result = R[0]
		return (self.report_val_result,self.text_result)

#---------------------------------[Funciones]------------------------------
#Agregar pruebas
def newProof():
	print "Captura los datos de la nueva prueba: "
	name=raw_input("Nombre: ")
	print "-En caso de multilples opciones de resultos separa con un \";\" -"
	aprovedText=raw_input("Resultados aprobatorios: ")
	notaprovedText=raw_input("Resultados no aprobatorios: ")
	command= ("""
		INSERT INTO Proof_Standar  VALUES(DEFAULT,%s, %s, %s);
		""",
		(name,aprovedText,notaprovedText))
	DB_execute(command,insert=True)
#Imprimir Reporte
def printReport(report_val_result,text_result):
	print "\n"
	if report_val_result:
		print "Reporte positivo: El total de las pruebas fueron exitosas"
	else:
		print "Resultado no satisfactorio: "
		print text_result
#Actualiza los cambios realizados en las pruebas en el formato de reporte, manda a llamar impresion y respalda en BD
def updateReport():
	commands = (
        """
        SELECT * from Proof_Standar;
        """
        )
	c=DB_execute(commands,select=True)
	#print c
	report = Report_class()
	for proof in c:
		new=Proof_Standar(proof[1],proof[2],proof[3])
		report.addProof(new)
	result = report.runTest()

	printReport(result[0],result[1])
	s=str(result[1])
	if not result[1]:
		s="Resultado no satisfactorio"
	command= ("""
		INSERT INTO report  VALUES(DEFAULT,%s, %s, %s);
		""",
		(result[0],s,datetime.now()))
	DB_execute(command,insert=True)
#Cambia propiedades en las pruebas ya existenntes
def alterProof():
	commands = (
        """
        SELECT name from Proof_Standar;
        """
        )
	c=DB_execute(commands,select=True)
	choise=0
	for option in c: 
		#print option[0]
		choise=choise+1
		print "\t"+str(choise)+")"+option[0]+"."
	ans=int(raw_input("Elije la prueba a modificar: "))
	while not(isinstance(ans,int)) or ans > choise or ans<1:
		print ans 
		print "Seleccione una respuesta segun los numeros en las opciones..."
		ans=raw_input("Elije la prueba a modificar: ")

	name=str(c[ans][0])

	print "De la prueba \""+name+"\" defina los nuevos valores para"
	aprovedText=raw_input("Resultados aprobatorios: ")
	notaprovedText=raw_input("Resultados no aprobatorios: ")
	commands = (
        """
        UPDATE  Proof_Standar SET  positive_outcome=%s,negative_outcome=%s  WHERE name=%s;
        """,(aprovedText,notaprovedText,name)
        )
	DB_execute(commands,insert=True)



if __name__ == '__main__':
	create_tables()
	insertDefaultData()
	updateReport()
	#newProof()
	pass
