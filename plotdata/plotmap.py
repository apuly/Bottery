import sqlite3
import math

class plotmap(object):
    """description of class"""
    def __init__(self, dbFile):
        self.db = dbFile
    
    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

    def getPlotsByName(self, playerName):
        self.cur.execute("""
                         SELECT X, Y
                         FROM plotdata
                         WHERE playername = ?
                         """, (playerName, ))
        return self.cur.fetchall()


    def getPlotsByUuid(self, uuid):
        self.cur.execute("""
                         SELECT X, Y
                         FROM plotdata
                         WHERE uuid = ?
                         """, (uuid, ))
        return self.cur.fetchall()

    def getOwnerByPlotCoords(self, x, y):
        self.cur.execute("""
                        SELECT playername
                        FROM plotdata
                        WHERE x = ? AND y = ?
                         """, (x, y,))
        return self.cur.fetchone()

    def getOwnerByPlayerCoords(self, xPlayer, yPlayer):
        devider = 256
        xPlot = math.floor(xPlayer/devider)
        yPlot = math.floor(yPlayer/devider)
        return self.getOwnerByPlotCoords(xPlot, yPlot)
