from flask import Flask,redirect, render_template, request,session
import math
import sqlite3
import re


def connect():
    x=sqlite3.connect("table.db",isolation_level=None)
    x.row_factory=sqlite3.Row
    return x
graph=[]
app=Flask(__name__)
app.secret_key = "logic_implication_table"

@app.route("/",methods=["POST","GET"])
def index():
        if request.method=="POST":
             session["error"]=None
             action=request.form.get("action")
             if action=="add":
                  with connect() as x:

                       if not(request.form.get("ps") or request.form.get("ns0") or request.form.get("ns1") or request.form.get("output")):
                          session["error"]="Fill the whole input"
                          return redirect("/")
                       ps=str(request.form.get("ps")).strip()
                       if ps.isalpha()==0 or len(ps)!=1:
                          session["error"]="State must be one letter"
                          return redirect("/")
                       ns0=str(request.form.get("ns0")).strip()
                       if ns0.isalpha()==0 or len(ns0)!=1:
                          session["error"]="State must be one letter"
                          return redirect("/")
                       ns1=str(request.form.get("ns1")).strip()
                       if ns1.isalpha()==0 or len(ns0)!=1:
                          session["error"]="State must be one letter"
                          return redirect("/")
                       output=str(request.form.get("output")).strip()
                       if re.search("^[01]+$",output)is None:
                          session["error"]="Output must be 1/2 digits with only 0's and 1's"
                          return redirect("/")
                       ps=ps.upper()
                       ns0=ns0.upper()
                       ns1=ns1.upper()
                       db=x.cursor()
                       print(output)
                       db.execute("""
                        CREATE TABLE IF NOT EXISTS transition(
                                  id INTEGER PRIMARY KEY NOT NULL,
                                  ps TEXT,
                                  ns0 TEXT,
                                  ns1 TEXT,
                                  output TEXT
                                  )
                                  """)
                       rows=db.execute("SELECT * FROM transition").fetchall()
                       for i in rows:
                           if i["ps"]==ps:
                               session["error"]="State already exists"
                               return redirect("/")


                       if(rows):
                            if len(output)!=len(rows[0]["output"]):
                                  session["error"]="Current State's Output type must be the same as the first row (Mealy/Moore) "
                                  return redirect("/")
                       db.execute("INSERT INTO transition (ps,ns0,ns1,output) VALUES (?,?,?,?)",(ps,ns0,ns1,output))
                       graph.append({
                           "ps":ps,
                           "ns0":ns0,
                           "ns1":ns1,
                           "output":output
                       })
             elif action=="remove":
                 session["error"]=""
                 with connect() as x:
                     db=x.cursor()
                     db.execute("""
                        CREATE TABLE IF NOT EXISTS transition(
                                  id INTEGER PRIMARY KEY NOT NULL,
                                  ps TEXT,
                                  ns0 TEXT,
                                  ns1 TEXT,
                                  output TEXT
                                  )
                                  """)
                     row=db.execute("SELECT * FROM transition").fetchall()
                     if len(row)==0:
                          session["error"]="Nothing to remove"
                          return redirect("/")
                     count=len(graph)
                     print(count)
                     deleted=db.execute("SELECT * FROM transition WHERE id=(SELECT MAX(id) FROM transition)").fetchone()
                     db.execute("DELETE FROM transition WHERE id=(SELECT MAX(id) FROM transition)")
                     if(deleted):
                         for i in graph:
                             if i["ps"]==deleted["ps"]:
                                 graph.remove(i)
                                 break










             return redirect("/")

        else:
            error=session.get("error")
            if error==None:
                error=""
            output_length=int()
            implication_table=[]
            sets=[]
            with connect() as x:
                db=x.cursor()
                db.execute("""
                        CREATE TABLE IF NOT EXISTS transition(
                                  id INTEGER PRIMARY KEY NOT NULL,
                                  ps TEXT,
                                  ns0 TEXT,
                                  ns1 TEXT,
                                  output TEXT
                                  )
                                  """)
                row=db.execute("SELECT * FROM transition WHERE id=1").fetchone()
                rows=db.execute("SELECT * FROM transition").fetchall()
                if row is None:
                    output_length=1
                else:
                    output_length=len(row["output"])
            count=len(rows)
            for i in range(0,count):
                if i==count-1:
                    break
                for j in range(0,i+1):
                    if i!=count-1:
                        if rows[i+1]["output"]!=rows[j]["output"]:
                            implication_table.append("X")
                        elif rows[i+1]["ns0"]==rows[j]["ns0"] and rows[i+1]["ns1"]!=rows[j]["ns1"]:
                            implication_table.append(f"{rows[i+1]["ns1"]}-{rows[j]["ns1"]}")
                        elif rows[i+1]["ns0"]!=rows[j]["ns0"] and rows[i+1]["ns1"]==rows[j]["ns1"]:
                            implication_table.append(f"{rows[i+1]["ns0"]}-{rows[j]["ns0"]}")
                        elif rows[i+1]["ns0"]!=rows[j]["ns0"] and rows[i+1]["ns1"]!=rows[j]["ns1"]:
                            implication_table.append(f"{rows[i+1]["ns0"]}-{rows[j]["ns0"]}/{rows[i+1]["ns1"]}-{rows[j]["ns1"]}")
                        elif rows[i+1]["ns0"]==rows[j]["ns0"] and rows[i+1]["ns1"]==rows[j]["ns1"]:
                            implication_table.append("✔")
            set1={}
            set2={}
            set3={}
            state1=str()
            state2=str()
            for i in range(0,len(implication_table)):

                for j in range(0,len(implication_table)):
                        if implication_table[j]=="X" or implication_table[j]=="✔" or implication_table[j].startswith(".X"):
                            continue
                        if len(implication_table[j])==7:
                            set1={implication_table[j].split("/")[0].split("-")[0],implication_table[j].split("/")[0].split("-")[1]}
                            set2={implication_table[j].split("/")[1].split("-")[0],implication_table[j].split("/")[1].split("-")[1]}
                        elif len(implication_table[j])==3:
                            set1={implication_table[j].split("-")[0],implication_table[j].split("-")[1]}
                        for k in range(0,len(implication_table)):
                                l=  int(  (-1+math.sqrt(1-(4*(-2*k))))/2  )
                                m=int( k-( int(l*(l+1)/2) ) )

                                state1=rows[m]["ps"]
                                state2=rows[l+1]["ps"]
                                set3={state1,state2}
                                if len(implication_table[j])==7:
                                    if (set1==set3 or set2==set3) and (implication_table[k]=="X" or implication_table[k].startswith(".X")):
                                        implication_table[j]=".X"+str(implication_table[j])
                                elif len(implication_table[j])==3:
                                    if (set1==set3) and (implication_table[k]=="X" or implication_table[k].startswith(".X")):
                                        implication_table[j]=".X"+str(implication_table[j])







            k=0
            for i in range(0,count):
                if i==count-1:
                    break
                for j in range(0,i+1):
                    try:
                        if i!=count-1:
                            state1=rows[j]["ps"]
                            state2=rows[i+1]["ps"]
                            set3={state1,state2}
                            if len(implication_table[k])==3:
                                set1={implication_table[k].split("-")[0],implication_table[k].split("-")[1]}
                                if set1==set3:
                                    implication_table[k]="✔"
                            k+=1
                    except IndexError:
                       break






            t=0
            for i in range(0,count):
                if i==count-1:
                    break
                for j in range(0,i+1):
                    if i!=count-1:
                       state1=rows[j]["ps"]
                       state2=rows[i+1]["ps"]
                    try:
                        if not (implication_table[int( (i+1)*i/2 ) +j].startswith("X") or implication_table[int( (i+1)*i/2 ) +j].startswith(".X")):

                                for k in sets:
                                    if state1 in k and state2 in k:
                                        break
                                    elif state1 in k and state2 not in k:
                                        k.add(state2)
                                        break
                                    elif state1 not in k and state2 in k:
                                        k.add(state1)
                                        break
                                else:
                                    sets.append(set())
                                    sets[t].add(state2)
                                    sets[t].add(state1)
                                    t+=1
                    except IndexError:
                        break

            partition=set()
            states=set()
            for i in sets:
                partition=partition.union(i)
            for i in rows:
                states.add(i["ps"])
            difference=states.difference(partition)
            for i in difference:
                sets.append(set())
                sets[t].add(i)
                t+=1
            results=[]
            alphabets=[chr(i) for i in range(65,65+26)]
            k=0
            t=0
            modified_sets=[]

            for i in range(0,len(sets)):
                modified_sets.append({})
                modified_sets[k]["ps"]=alphabets[k]
                modified_sets[k]["set"]=sets[i]
                k+=1

            for i in modified_sets:
                results.append(dict())
                results[t]["ps"]=i["ps"]
                present_state=list(i["set"])[0]
                for j in rows:
                    if j["ps"]==present_state:
                        next_state_0=j["ns0"]
                        next_state_1=j["ns1"]
                        results[t]["output"]=j["output"]
                        break
                for j in modified_sets:
                    if next_state_0 in j["set"]:
                        results[t]["ns0"]=j["ps"]
                    if next_state_1 in j["set"]:
                        results[t]["ns1"]=j["ps"]
                t+=1

                for i in results:
                    try:
                        list(i.keys()).index("ns1")
                        list(i.keys()).index("ns0")
                    except ValueError:
                        print(f"Error: {error}")
                        if error=="" or error is None:
                            error="Incomplete Table"



            return render_template("index.html",graph=rows,count=count,output_length=output_length,implication_table=implication_table,sets=sets,results=results,error=error)
