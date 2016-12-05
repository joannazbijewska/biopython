# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 18:19:28 2016

@author: michalkarlicki, gruszka, asiazbijewska
"""
import xlrd
import csv
import urllib
import requests
from lxml import html
import re

def csv_from_excel():
    """ xls files converter"""
    wb = xlrd.open_workbook('NDB_updated.xls')
    sh = wb.sheet_by_name('sheet_1')
    your_csv_file = open('NDB_database.csv', 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    your_csv_file.close()

def database_read(pdb_id):
    with open("NDB_database.csv","r") as f:
        otw = csv.reader(f)
        for i in otw:
            if i[1] == pdb_id:
                return i


def search_blast_pdb(sequence):
    urldb = "http://www.rcsb.org/pdb/rest"
    url = urldb+"/getBlastPDB1?sequence={}&eCutOff=10.0&matrix=BLOSUM62&outputFormat=html".format(sequence)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    sequence = tree.xpath('//pre/pre/text()')
    pattern = "([A-Z,0-9])\w+"
    list_pdb_id = []
    for i in sequence:
        match = re.search(pattern, i)
        if match:
            if len(match.group(0)) == 4:
                list_pdb_id.append(match.group(0))
    if len(list_pdb_id) > 3:
        return list_pdb_id[0:3]
    else:
        return list_pdb_id

def check_base(pdb_id):
    with open("NDB_database.csv","r") as f:
        otw = csv.reader(f)
        for i in otw:
            if i[1] == x:
                return True

def get_from_db_via_seq(sequence):
    pdb_ids = search_blast_pdb(sequence) #zakładając pierwszy jako właściwy
    for i in pdb_ids:
        if check_base(i) is True:
            return i
        else:
            return sequence[0]



class Nucleic_acid_database():

    def __init__(self, pdb_id):
        self.pdb_id = pdb_id

    def download_database(self):
        """ Database updater"""
        url ="http://ndbserver.rutgers.edu"
        url1 = url+"/service/ndb/atlas/gallery/rna?polType=onlyRna&rnaFunc=all&protFunc=all&strGalType=rna&expMeth=all&seqType=all&galType=table&start=0&limit=50"
        query = requests.get(url1)
        tree = html.fromstring(query.content)
        database_link = tree.xpath('//tr/td/h2/span/a[@id]/@href')
        urllib.urlretrieve(url+database_link[0], "NDB_updated.xls")
        csv_from_excel()
        return " NDB Database was updated and converted to csv file"

    def database_read_metadata(self):
        """ Metadata reader """
        with open("NDB_database.csv","r") as f:
            otw = csv.reader(f)
            for i in otw:
                if i[1] == self.pdb_id:
                      meta = i

        return "Pdb id: {pdb}\nNbd id: {nbd}\nName of the structure: {nazwa}\nTitle of the publication: {title}\nDate of publication: {data}\nAuthors: {aut}\nMethod: {method}\nResolution: {rez}\nR value: {rvl}".format(pdb = meta[1], nazwa = meta[3], nbd = meta[0], title = meta[6], data = meta[4], aut = meta[5], method = meta[8], rez = meta[9], rvl = meta[10])

    def structure_download(self):
        """ Structure download pdb format"""
        urldb = "http://ndbserver.rutgers.edu"
        pdb_id = self.pdb_id.lower()
        url1 = urldb+"/files/ftp/NDB/coordinates/na-nmr/pdb{}.ent.gz.".format(pdb_id)
        url2 = urldb+"/files/ftp/NDB/coordinates/na-biol/{}.pdb1".format(pdb_id)
        r = requests.get(url1)
        if r.status_code != 404:
            urllib.urlretrieve(url1, "{}.ent.gz.".format(pdb_id))
        else:
            urllib.urlretrieve(url2, "{}.pdb1".format(pdb_id))

        print "PDB file download {}".format(pdb_id)

        print "PDB file download...".format(pdb_id)


    def sequence_view(self):
        """ Sequence view """
        urldb = "http://ndbserver.rutgers.edu"
        url = urldb+"/service/ndb/atlas/summary?searchTarget={}".format(self.pdb_id)
        page = requests.get(url)
        tree = html.fromstring(page.content)
        sequence = tree.xpath('//p[@class="chain"]/text()')
        return sequence[0]

    def fasta_sequence(self):
        pdb_id = self.pdb_id
        sekwencja = self.sequence_view()
        plik = open("plik_fasta_{}.fasta".format(pdb_id),"w")
        plik.write(">"+pdb_id+"\n"+sekwencja) #??????
        plik.close()

    def metadata_to_file(self):
        with open("NDB_database.csv","r") as f:
            otw = csv.reader(f)
            for i in otw:
                if i[1] == self.pdb_id:
                      meta = i
        f = open("report_{}".format(self.pdb_id), "w")
        metadata = "Pdb id: {pdb}\nNbd id: {nbd}\nName of the structure: {nazwa}\nTitle of the publication: {title}\nDate of publication: {data}\nAuthors: {aut}\nMethod: {method}\nResolution: {rez}\nR value: {rvl}".format(pdb = meta[1], nazwa = meta[3], nbd = meta[0], title = meta[6], data = meta[4], aut = meta[5], method = meta[8], rez = meta[9], rvl = meta[10])
        f.write("RNA structure from NBD\n"+metadata)
        f.close()

class via_sequence(Nucleic_acid_database):

    def __init__(self, sequence = None, pdb_id = None):
        self.sequence = sequence
        if pdb_id is None:
            self.pdb_id = get_from_db_via_seq(self.sequence)
        else:
            self.pdb_id = pdb_id



proba = via_sequence(pdb_id = "5SWE")
print proba.fasta_sequence()
