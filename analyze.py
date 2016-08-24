#!/usr/bin/env python

import sqlite3, sys
from s2sphere import CellId
from utils import get_pokenames

def gen_db(dbfile):

    dbin = sqlite3.connect(dbfile)
    dbout = sqlite3.connect(':memory:'); dbcur = dbout.cursor()
    dbcur.execute("CREATE TABLE encount (spawn VARCHAR PRIMARY KEY, poke INT, count INT DEFAULT 0)")
    
    for i in range(151):
        
        encs = [x[0] for x in dbin.cursor().execute("SELECT spawn_id FROM encounters "
                        "WHERE spawn_id IS NOT NULL AND pokemon_id = %d" % i).fetchall()]
        
        if len(encs) > 0:
        
            
            for e in encs:
                dbcur.execute("INSERT OR IGNORE INTO encount (spawn, poke) VALUES ('{}',{})".format(e,i))
                dbcur.execute("UPDATE encount SET count = count + 1 WHERE spawn = '%s'" % e)
                
    dbout.commit()
    return dbout

def gen_csv(db, filename):
    
    f = open(filename,'w')
    pname = get_pokenames('pokes.txt')
    f.write('spawn_id, pokemon_id, pokemon_name, count, latitude, longitude')
    
    for i in range(151):
    
        spwns = db.cursor().execute("SELECT spawn, count FROM encount "
                        "WHERE poke = %d AND count > 1 ORDER BY count DESC" % i).fetchall()
        
        if len(spwns) > 0:
            for s,c in spwns:
                _ll = CellId.from_token(s).to_lat_lng()
                lat, lng, = _ll.lat().degrees, _ll.lng().degrees
                f.write("{},{},{},{},{},{}\n".format(s,i,pname[i],c,lat,lng))
                
    print('Done!')

def main():
    db = gen_db('db2.sqlite')
    
    if sys.argv[1] == 'export' and sys.argv[2] == 'csv':
        gen_csv(db, sys.argv[3])
    
if __name__ == '__main__':
    main()