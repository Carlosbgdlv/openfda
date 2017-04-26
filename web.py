# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Carlos Barquero Gómez de la Venta
#
#


import http.client
import http.server
import socketserver
import json

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):


    def do_GET(self):
        client=OpenFDAClient()
        html=OpenFDAHTML()
        parser=OpenFDAParser()
        main_page=False
        is_eventdrug=False
        is_searchdrug=False
        is_eventcompany=False
        is_searchcompany=False
        is_eventsex=False
        is_error=False
        is_redirect=False
        is_secret=False
        is_found=False
        if self.path == '/':
            main_page = True
            is_found=True


        elif "searchDrug" in self.path:
            is_searchdrug=True
            is_found=True
        elif "listDrugs" in self.path:
            is_eventdrug=True
            is_found=True
        elif "searchCompany" in self.path:
            is_searchcompany=True
            is_found=True
        elif "listCompanies" in self.path:
            is_eventcompany=True
            is_found=True
        elif "listGender" in self.path:
            is_eventsex=True
            is_found=True
        elif "secret" in self.path:
            is_secret=True
            is_found=True
        elif "redirect" in self.path:
            is_redirect=True
            is_found=True
        else:
            is_error=True

        if is_secret:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Login required"')
        elif is_redirect:
            self.send_response(302)
            self.send_header('Location','/')
        elif is_found:
            self.send_response(200)
            self.send_header('Content-type','text/html')
        else:
            self.send_response(404)
            self.send_header('Content-type','text/html')


        self.end_headers()



        html_mainpage=html.get_main_page()

        if main_page:
            self.wfile.write(bytes(html_mainpage, "utf8"))

        elif is_eventsex:
            Limites=self.get_any_drug()
            event=client.get_event(Limites)
            lista=parser.get_patientsex(event)
            html=html.html_patientsex(lista)
            self.wfile.write(bytes(html, "utf8"))


        elif is_eventdrug:
            Limites=self.get_any_drug()
            event=client.get_event(Limites)
            event1=event['results']
            lista=[]
            for event in event1:
                event2 = (event['patient']['drug'][0]['medicinalproduct'])
                event3=json.dumps(event2)
                lista+=[event3]
            html_medicine=html.get_event_html(lista)
            self.wfile.write(bytes(html_medicine, "utf8"))


        elif is_searchdrug:
            drug=self.get_any_drug()
            events=client.get_medicamento(drug)
            search2=parser.get_company(events)
            html_final=html.html_medicamento(search2)
            self.wfile.write(bytes(html_final,"utf8"))
            #return

        elif is_eventcompany:
            Limites=self.get_any_drug()
            event=client.get_event(Limites)
            event1=event['results']

            lista=[]
            for event in event1:
                event2 = event['companynumb']
                event3=json.dumps(event2)
                lista+=[event3]
            html_medicine=html.html_medicamento(lista)
            self.wfile.write(bytes(html_medicine, "utf8"))


        elif is_searchcompany:
            drug=self.get_any_drug()
            events=client.get_companies(drug)
            search2=parser.get_drugs(events)
            html_final=html.get_event_html(search2)
            self.wfile.write(bytes(html_final,"utf8"))

        else:
            self.wfile.write(bytes(html.get_html_error(), "utf8"))

        return

    def get_any_drug(self):
        drug1=self.path.split("=")[1]
        return drug1



class OpenFDAParser():

    def get_company(self, events):

        company=[]
        for event in events['results']:
            company  += [event['companynumb']]
        return company

    def get_drugs(self, events):

        company=[]
        for event in events['results']:
            company+=[event["patient"]["drug"][0]["medicinalproduct"]]
        return company

    def get_patientsex(self, event):
        lista=[]
        event1=event['results']
        for event in event1:
            event2=event['patient']['patientsex']
            event3=json.dumps(event2)
            lista+=[event3]
        return lista



class OpenFDAClient():
    OPENFDA_API_URL = "api.fda.gov"
    OPENFDA_API_EVENT = "/drug/event.json"
    OPENFDA_API_LYRICA = "/drug/event.json?search=patient.drug.medicinalproduct="
    OPENFDA_API_COMPANY = "/drug/event.json?search=companynumb:"




    def get_event(self, limit):
    ###
    # GET EVENT
    ##

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_EVENT+"?limit="+ limit)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)

        data1 = r1.read()
        data1 = data1.decode("utf8")
        data2 = json.loads(data1)
        return data2


    def get_medicamento(self, drug):

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_LYRICA +drug+ "&limit=10")
        r1 = conn.getresponse()
        print(r1.status, r1.reason)

        data1 = r1.read()
        data1 = data1.decode("utf8")
        data2 = json.loads(data1)
        return data2

    def get_companies(self, drug):

        conn = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        conn.request("GET", self.OPENFDA_API_COMPANY +drug+ "&limit=10")
        r1 = conn.getresponse()
        print(r1.status, r1.reason)

        data1 = r1.read()
        data1 = data1.decode("utf8")
        data2 = json.loads(data1)
        return data2



class OpenFDAHTML():
    def get_main_page(self):
        html = """
        <html>
            <head>
                <title>OpenFDA Cool App</title>
            </head>
            <body>
                <h1>OpenFDA Client</h1>
                <form method='get' action='listDrugs'>

                    <input type='submit' value = "Medicamentos">
                    </input>
                    Limites:
                    <input name='limite' type = "text">
                    </input>
                </form>

                <form method='get' action='searchDrug'>
                    Drug name:
                    <input name="drug"  type="text">
                    </input>

                    <input type='submit' value = "Obtener fabricantes">
                    </input>
                </form>

                <form method='get' action='listCompanies'>

                    <input type='submit' value = "Empresas">
                    </input>
                     Limites:
                    <input name='limite' type = "text">
                    </input>
                </form>

                <form method='get' action='searchCompany'>
                    Company name:
                    <input name="company"  type="text">
                    </input>
                    <input type='submit' value = "Obtener medicamentos">
                    </input>
                </form>

                <form method='get' action='listGender'>

                    <input type='submit' value = "Genero">
                    </input>
                    Limites:
                    <input name='limite' type = "text">
                    </input>
                </form>



        </body>
        </html>
            """
        return html


    def get_event_html(self,lista):
        html_event = """
        <html>
        <head></head>
        <body>
            <h1> MEDICAMENTOS </h1>
            <ol>
                """


        for i in lista:
                html_event+="<li>"+i+"</li>"
        html_event+= """
               </ol>
            </body>
            </html>
                """

        return html_event



    def html_medicamento(self, lista):

        html_event="""
        <html>
            <head></head>
            <body>
                <h1>EMPRESAS</h1>
                <ol>
        """

        for i in lista:
            html_event+="<li>"+i+"</li>"
        html_event += """     </ol>
            </body>
        </html>
        """

        return html_event

    def html_patientsex(self, lista):
        html_event="""
        <html>
            <head></head>
            <body>
                <h1>GENEROS</h1>
                <ol>
        """

        for i in lista:
            html_event+="<li>"+i+"</li>"
        html_event += """     </ol>
            </body>
        </html>
        """
        return html_event



    def get_html_error(self):
        html_event_error='''
        <html>
            <head>
                <title>error 404</title>
            </head>
            <body>
            <h1>ERROR 404
            NOT FOUND
            </h1>
            </body>
        </html>
        '''
        return html_event_error
