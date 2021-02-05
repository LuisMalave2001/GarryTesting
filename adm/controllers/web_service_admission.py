import json

from odoo import http

# Updated 2020/12/14
# By Luis
# Just some clean up

class AdmisionController(http.Controller):
    """ Controlador encargado de devolver datos de las admisiones,
    para insertarlas en FACTS
    """

    # csrf: hay que añadir este parametro si es POST, PUT, etc, para todo
    # menos para GET.
    @http.route("/admission/adm", auth="public", methods=["GET"], cors='*')
    def get_adm_uni(self, **params):
        """ Definiendo la url desde donde va ser posible acceder, tipo de
        metodo,
        cors para habiltiar accesos a ip externas.
        """

        allowed_urls = (http.request.env['ir.config_parameter'].sudo()
                        .get_param('allow_urls', ''))

        origin_url = '-1'

        # Array con los campos del alumno y de las familias y los partners
        partner_fields = ["company_type", "type", "first_name",
                          "middle_name", "last_name", "street", "street2",
                          "city", "state_id", "zip", "country_id",
                          "function", "phone", "mobile", "email", "website",
                          "title", "lang", "category_id", "vat",
                          "company_id", "citizenship",
                          "identification", "marital_status",
                          "parental_responsability",
                          "title", "work_address", "work_phone", "child_ids",
                          "user_id", "person_type", "grade_level_id",
                          "homeroom", "student_status",
                          "comment_facts", "facts_id", "facts_id_int",
                          "is_in_application", "application_id",
                          "inquiry_id", "gender", "relationship_ids",
                          "family_ids"]

        # DATOS DE LA APPLICATION        

        # Crea una variable con el modelo desde donde se va a tomar la
        # información
        ApplicationEnv = http.request.env['adm.application'].sudo()

        # filtro del modelo: status = done y el checkBox Imported = False
        search_domain = [("status_id.type_id", "in", ["done", "stage"])]

        # Tomar informacion basado en el modelo y en el domain IDS
        application_record = ApplicationEnv.search(search_domain)

        # Obtienes la información basada en los ids anteriores y tomando en
        # cuenta los campos definifos en la funcion posterior
        application_values = application_record.read(
            ["id", "status_type", "first_name", "middle_name", "last_name",
             "contact_time_id", "grade_level", "gender", "father_name",
             "mother_name", "task_ids", "street", "city", "state_id", "zip",
             "country_id", "home_phone", "phone", "email", "date_of_birth",
             "citizenship",
             "first_language", "first_level_language", "second_language",
             "second_level_language", "third_language", "third_level_language",
             "previous_school_ids", "doctor_name", "doctor_phone",
             "doctor_address", "permission_to_treat", "blood_type",
             "medical_conditions_ids", "medical_allergies_ids",
             "medical_medications_ids",
             "relationship_ids", "partner_id", "name", "house_address_ids",
             "sibling_ids",
             ])

        # recorremos el array y vamos tratando los datos. Se modifica el
        # formato del for: se añade index y enumerate para poder hacer
        # busquedas
        # por el index, esto se usa en las familias.
        for index, record in enumerate(application_values):
            application_id = application_record[index].sudo()

            # Convertir fechas a string
            record["date_of_birth"] = (application_id.date_of_birth
                                       .strftime('%m/%d/%Y') if
                                       application_id.date_of_birth else '')

            # SchooCode
            if record["grade_level"]:
                record["SCName"] = (application_id.grade_leve
                                    .school_code_id.name) or []

            # Sacamos datos de los Horarios de partner   
            # Array para los Horarios de partner
            if record["contact_time_id"]:
                record["horariopartnerDatos"] = (application_id
                                                 .contact_time_id
                                                 .read(["name",
                                                        "from_time",
                                                        "to_time"])) or []

            # Sacamos datos de los Hermanos    
            # Array para los Hermanos
            record["hermanosDatos"] = (application_id.sibling_ids
                                       .read(["name", "age", "school"]))

            # Array para las task
            record["task"] = (application_id.task_ids
                              .read(["name", "description", "display_name"]))

            # Sacamos datos de las relationship    
            # Array para las relationships  
            record["relationship"] = (application_id.relationship_ids
                                      .read(["partner_2",
                                             "relationship_type"]))

            # Sacamos datos del previous school
            # if record["previous_school_ids"]:

            # Array para los datos del colegio previo    
            datosPrev_values = (application_id.previous_school_ids
                                .read(["application_id",
                                       "id",
                                       "name",
                                       "street",
                                       "zip",
                                       "country_id",
                                       "from_date",
                                       "to_date",
                                       "extracurricular_interests",
                                       "city", "state_id",
                                       "grade_completed"
                                       ]))

            # Recorremos los datos obtenidos y transformamos las fechas para
            # evitar errores
            for record_school in datosPrev_values:
                # Convertir fechas a string
                record_school["from_date"] = (record_school["from_date"]
                                              .strftime('%m/%d/%Y')
                                              if record_school["from_date"]
                                              else '')

                record_school["to_date"] = (record_school["from_date"]
                                            .strftime('%m/%d/%Y')
                                            if record_school["to_date"]
                                            else '')

            record["previousSchool"] = datosPrev_values

            # Array para los datos de las direcciones    
            record["address"] = (application_id.house_address_ids
                                 .read(["name",
                                        "country_id",
                                        "state_id",
                                        "street",
                                        "zip",
                                        ]))

            # Sacamos datos de las medicals conditions
            # if record["medical_conditions_ids"]:  

            # Array para los datos medicos Conditions  
            record["medicalConditions"] = (application_id
                                           .medical_conditions_ids
                                           .read(["name", "comment"]))

            # Sacamos datos de las medicals allergies
            # if record["medical_allergies_ids"]:

            # Array para los datos medicos Allergies  
            record["medicalAllergies"] = (application_id
                                          .medical_allergies_ids
                                          .read(["name", "comment"]))

            # Sacamos datos de las medicals medications
            # if record["medical_medications_ids"]:

            # Array para los datos medicos Medications  
            record["medicalMedications"] = (application_id
                                            .medical_medications_ids
                                            .read(["name", "comment"]))

            # DATOS DEL ALUMNO

            # Sacamos datos del alumno
            # if record["partner_id"]:

            # Array para los datos alumnos  
            # Tomar informacion basado en el modelo y en el domain IDS
            application_partner_id = application_id.partner_id
            record["alumnoDatos"] = application_partner_id.read(partner_fields)

            # DATOS DE LA FAMILIA              
            # Array para los datos de cada familia  
            record["familiaDatos"] = []

            family_id = application_partner_id.family_ids[0]
            record["familiaDatos"] = family_id.read(partner_fields)

            # DATOS DE LOS CONTACTOS
            # Array para los datos de cada partner  
            family_member_ids = (family_id.member_ids.filtered(
                lambda member_id: member_id != application_partner_id))
            record["partnerDatos"] = family_member_ids.read(partner_fields)

            # DATOS DE LOS FICHEROS              
            # Array para los datos de cada fichero de la aplicacion  
            record["datosFicheros"] = []

            # crea una variable con el modelo desde donde se va a tomar la
            # información
            attachments = http.request.env['ir.attachment'].sudo()

            # filtro del modelo basados en parametros de la url
            # search_domain_attach =

            # Tomar informacion basado en el modelo y en el domain IDS
            # attachments_record = attachments.search(search_domain_attach)

            # Obtienes la información basada en los ids anteriores y tomando
            # en cuenta los campos definifos en la funcion posterior
            # mimetype: tpo de archivo, datas: arhivo en binario
            # attachments_values = attachments_record.read(["id", "name"])

            # record["datosFicheros"] = json.dumps(attachments_values)

        # pintar la información obtenida, esto lo utilizamos para parsearlo
        # en el ajax.
        return json.dumps(application_values)

    @http.route("/admission/adm_insertId", auth="public", methods=["POST"],
                cors='*', csrf=False)
    # define una funcion principal 
    def insert_id(self, **kw):
        data = json.loads(kw["data"])
        for itemData in data:
            # itemData["odooId"]
            # itemData["factsId"]
            application = http.request.env['res.partner'].sudo()

            # Con browse podemos buscar todo un array un array y juntamos
            #  las lineas de arriba y lade abajo que estan comentadas
            application_record = application.browse([itemData["odooId"]])

            # Obtienes la información basada en los ids anteriores y tomando
            # en cuenta los campos definifos en la funcion posterior
            # application_values = application_record.partner_id

            # Cambiamos application_values por application_record debido al
            # cambio de la linea 294
            application_record.write({
                'facts_id': itemData["factsId"]
                })

        return json.dumps(data)
