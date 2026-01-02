from flask import Flask, render_template, request, redirect, url_for, session
import jinja2
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


app=Flask(__name__)
app.secret_key="ejhfv"




def dbconn():
    conn=sqlite3.Connect('database.sqlite')
    return conn


@app.route('/',methods=['POST','GET'])
def index():
    session.clear()
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")
        
        conn = dbconn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("select user_id from users where username=?",(username,))
            userid=cursor.fetchone()[0]
            session.permanent=True
            session['user_id'] = userid
        
            return redirect(url_for('user_home',name=username))
        else:
            return render_template("login.html")

    return render_template("login.html")



@app.route('/register', methods=['POST', 'GET'])
def reg():

    if request.method == "POST":
        conn = dbconn()
        cursor = conn.cursor()

        username = request.form.get("name")
        password = request.form.get("password")

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route('/dashboard/<string:name>',methods=["POST","GET"])
def user_home(name):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if name!='Administrator':
        cursor=dbconn().cursor()
        cursor.execute("select user_id from users where username=?",(name,))
        usid=cursor.fetchone()[0]
        
        cursor.execute("""SELECT parking_spot.id, parking_lot.prime_loc_name, reserve_spot.vehicle_no, reserve_spot.parking_time ,reserve_spot.leave_time
                       FROM parking_spot INNER JOIN parking_lot  ON parking_spot.lot_id = parking_lot.id 
                       INNER JOIN  
                       reserve_spot  ON reserve_spot.spot_id = parking_spot.id 
                       WHERE  reserve_spot.user_id = ?; """,(usid,))
        
        data=cursor.fetchall()
        details=[]
        if request.method=="POST":
            searched=request.form.get('location')
            
            cursor.execute("""SELECT 
                                ps.id, 
                                pl.prime_loc_name, 
                                pl.pincode, 
                                ps.status
                                FROM 
                                parking_spot ps
                                JOIN 
                                parking_lot pl ON ps.lot_id = pl.id
                                WHERE 
                                ps.status = 'A' AND 
                                ps.id = (
                                SELECT MIN(ps2.id)
                                FROM parking_spot ps2
                                JOIN parking_lot pl2 ON ps2.lot_id = pl2.id
                                WHERE 
                                ps2.status = 'A' AND 
                                pl2.prime_loc_name = pl.prime_loc_name) 
                                AND pl.prime_loc_name LIKE ?""",('%'+searched+'%',))
            details=cursor.fetchall()

            if not details:
                try:
                    cursor.execute("""SELECT 
                                ps.id, 
                                pl.prime_loc_name, 
                                pl.pincode, 
                                ps.status
                                FROM 
                                parking_spot ps
                                JOIN 
                                parking_lot pl ON ps.lot_id = pl.id
                                WHERE 
                                ps.status = 'A' AND ps.id=
                               (select min(ps2.id) from parking_spot ps2 
                               join parking_lot pl2 on pl2.id=ps2.lot_id 
                               where 
                               ps2.status='A' 
                               and 
                               pl2.prime_loc_name=pl.Prime_loc_name) and pl.pincode=?""",(int(searched),))
                    details=cursor.fetchall()
                except:
                    details=[]
                
            
        return render_template('dashboard_user.html',name=name , locdata=details , data=data , usid=usid)
    else:
        conn=dbconn()
        cursor=conn.cursor()
        cursor.execute('select * from parking_lot')
        parking_lot=cursor.fetchall()
        all_parking=[]
        occ=[]
        total=[]
        tot_occ=0
        loc=[]
        
        for i in parking_lot:
            
            id=i[0]
            cursor.execute('select * from parking_spot , parking_lot on parking_spot.lot_id=parking_lot.id where lot_id=?',(int(id),))
            park=cursor.fetchall()
            parking=[list(row) for row in park]
            tot_spot=len(parking)
            total.append(tot_spot)
            all_parking.append(parking)
            cursor.execute("select prime_loc_name from parking_lot where id=?",(id,))
            loc_na=cursor.fetchone()
            loc_name=loc_na[0]
            loc.append(loc_name)
            tot_occ=0
            for j in parking:
                if j[2]=="o" or j[2]=="O":
                    tot_occ+=1
            occ.append(tot_occ)

            
            cursor.execute("select * from parking_lot")
            lots=cursor.fetchall()

        return render_template('dashboard_admin.html', name=name , occ=occ , total=total , lots=all_parking , location=loc)
    

@app.route('/add_card',methods=['POST','GET'])
def add_card():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method=="POST":
        location=request.form.get('location')
        pincode=request.form.get('pincode')
        price=request.form.get('price')
        max_spots=int(request.form.get('spots'))
        conn=dbconn()
        cursor=conn.cursor()
        cursor.execute('insert into parking_lot (prime_loc_name,max_no_spots,price,pincode) values(?,?,?,?)',(location,max_spots,price,pincode))
        cursor.execute("select id from parking_lot where prime_loc_name=? and pincode=?",(location,pincode))
        lot_num=cursor.fetchone()
        lot_num=lot_num[0]
        for i in range (0,max_spots):
            cursor.execute("insert into parking_spot (lot_id,status) values(?,?)",(lot_num,"A"))

        conn.commit()
        conn.close()
        return redirect(url_for('user_home',name="Administrator"))

    return render_template('add_card.html')

@app.route('/delete/<string:locname>')
def delete(locname):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select id from parking_lot where prime_loc_name=?",(locname,))
    id=cursor.fetchone()
    id=id[0]
    cursor.execute("select count(*) from parking_spot where lot_id=? and status='O' ",(id,))
    occupied=cursor.fetchone()[0]
    if occupied>0:
        return redirect(url_for('user_home',name="Administrator"))
    else:
        cursor.execute("delete from parking_lot where prime_loc_name=?",(locname,))
        cursor.execute("delete from parking_spot where lot_id=?",(id,))
        conn.commit()
        conn.close()
        return redirect(url_for('user_home',name="Administrator"))


@app.route('/edit/<string:locname>', methods=["POST","GET"])
def edit(locname):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select max_no_spots,price,pincode,id from parking_lot where prime_loc_name=?",(locname,))
    details=cursor.fetchone()
    max_spots=details[0]
    old_spots=int(max_spots)
    price=details[1]
    pincode=details[2]
    id=details[3]
    location=locname
    cursor.execute("select count(*) from parking_spot ps join parking_lot pl on pl.id=ps.lot_id where pl.prime_loc_name=? and ps.status='O'",(locname,))
    diff=cursor.fetchone()[0]

    if request.method=="POST":
        location=request.form.get('location')
        pincode=int(request.form.get('pincode'))
        price=int(request.form.get('price'))
        spots=int(request.form.get('spots'))
        if spots>old_spots:
            for i in range (1,spots-old_spots+1):
                cursor.execute("insert into parking_spot (lot_id,status) values(?,?)",(id,"A"))
                
            
        elif old_spots>spots:
            cursor.execute("select count(*) from parking_spot where status='A' and lot_id=?",(id,))
            avail=cursor.fetchone()
            available=avail[0]
            if available>=spots:
                cursor.execute("delete from parking_spot where id in(select id from parking_spot where lot_id=? and status='A' limit ?)",(id,available-spots) )
                


        cursor.execute("update parking_lot set prime_loc_name=? , pincode=? , price=? , max_no_spots=? where id=?",(location,pincode,price,spots,id))
        conn.commit()
        conn.close()
        return redirect(url_for('user_home',name='Administrator'))
    
    conn.commit()
    conn.close()
    
    return render_template('edit_card.html', max_spots=max_spots , price=price , pincode=pincode , location=location , diff=diff )

@app.route('/book/<int:id>/<int:usid>/<string:name>',methods=["POST","GET"])
def book(id,usid,name):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method=="POST":
        
        spot_id=request.form.get('spot_id')
        user_id=request.form.get('user_id')
        vehicle_no=request.form.get('vehicle_no')
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn=dbconn()
        cursor=conn.cursor()
        cursor.execute("insert into reserve_spot ( spot_id,user_id,parking_time,vehicle_no) values(?,?,?,?)",(spot_id,user_id,now,vehicle_no))
        cursor.execute("update parking_spot set status='O' where id=?",(spot_id,))
        cursor.execute("select username from users where user_id=?",(usid,))
        name=cursor.fetchone()[0]
        conn.commit()
        return redirect(url_for('user_home',name=name))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select lot_id from parking_spot where id=?",(id,))
    lot_i=cursor.fetchone()
    lot_id=lot_i[0]
    
    
    return render_template('booking.html', spot_id=id , lot_id=lot_id , user_id=usid , name=name)

@app.route('/release/<int:id>',methods=["POST","GET"])
def release(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select pl.price from parking_lot pl join parking_spot ps on ps.lot_id=pl.id where ps.id=? ",(id,))
    pric=cursor.fetchone()
    price=pric[0]
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""SELECT 
    vehicle_no, 
    parking_time, 
    CAST((julianday(?) - julianday(parking_time)) * 24 AS INTEGER) AS diff,
    CASE 
        WHEN CAST((julianday(?) - julianday(parking_time)) * 24 AS INTEGER) < 1 THEN ? 
        ELSE CAST((julianday(?) - julianday(parking_time)) * 24 AS INTEGER) * ?
    END AS cost
    FROM reserve_spot 
    WHERE spot_id = ? and leave_time is null""",(now,now,price,now,price,id))
    data=cursor.fetchone()

    usid=session['user_id']
    cursor.execute("select username from users where user_id=?",(usid,))
    na=cursor.fetchone()
    name=na[0]
    if request.method=="POST":
        cursor.execute(""" update parking_spot set status='A' where id=? """,(id,))
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("update reserve_spot set leave_time=? where spot_id=?",(now,id))
        conn.commit()
        conn.close()
        return redirect(url_for('user_home',name=name))
        


    return render_template('release.html',id=id,data=data , now=now , name=name)

@app.route('/dashboard/Administrator/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select  distinct r.vehicle_no , u.username , u.user_id from users u , reserve_spot r on u.user_id=r.user_id")
    data=cursor.fetchall()
    total=len(data)


    return render_template('users.html' , data=data , length=total)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/logout')
def logout():

    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard/summary/<int:usid>/<string:nme>')
def user_summary(usid,nme):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select pl.prime_loc_name , sum(CAST((julianday(rs.leave_time) - julianday(rs.parking_time)) * 1440 AS INTEGER)) as total from parking_lot pl join parking_spot ps on ps.lot_id=pl.id join reserve_spot rs on rs.spot_id=ps.id where rs.user_id=? and rs.leave_time is not null group by pl.prime_loc_name ",(usid,))
    data=cursor.fetchall()
    x=[ ]
    for i in data:
        a=i[0]
        b=a.split(",",1)[0].strip()
        x.append(b)
    y=[b[1] for b in data ]
    plt.bar(x,y)
    plt.xlabel("Location")
    plt.ylabel("Time in minutes")
    plt.title("Parking duration by lot")
    plt.xlim(-0.5,)
    plt.ylim(0,)
    plt.tight_layout()
    plt.xticks(rotation=20)
    plt.savefig("static/lot_duration.png")
    plt.close()
    return render_template('user_summary.html' , name=nme)

@app.route('/dashboard/<int:id>' , methods=["GET","POST"])
def view(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method=="POST":
        return redirect(url_for('detailed_view',id=id))
    conn=dbconn()
    cursor=conn.cursor()
    
    cursor.execute("select status from parking_spot where id=?",(id,))
    status=cursor.fetchone()[0]
    return render_template('view.html' , status=status , id=id) 

@app.route('/delete_spot/<int:id>', methods=["GET","POST"])
def del_spot(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("select status from parking_spot where id=?",(id,))
    status=cursor.fetchone()[0]
    if status=='A':
        cursor.execute("delete from parking_spot where id=?",(id,))
        conn.commit()
    else:
        return 
        
    return redirect(url_for('user_home',name='Administrator'))

@app.route('/dashboard/summary')
def admin_summary():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    cursor.execute("""SELECT pl.prime_loc_name, 
                    sum(CASE 
                    when CAST((julianday(leave_time) - julianday(parking_time)) * 24 AS INTEGER) < 1 THEN pl.price 
                    ELSE CAST((julianday(leave_time) - julianday(parking_time)) * 24 AS INTEGER) * pl.price END) 
                    AS cost
                    FROM reserve_spot rs join parking_spot ps 
                    on ps.id=rs.spot_id 
                    join parking_lot pl on pl.id=ps.lot_id where rs.leave_time is not null
                    group by ps.lot_id""")

    data=cursor.fetchall()
    x=[ ]
    for i in data:
        a=i[0]
        b=a.split(",",1)[0].strip()
        x.append(b)
    y=[b[1] for b in data ]
    plt.bar(x,y)
    plt.xlabel("Location")
    plt.ylabel("Money from lots ")
    plt.title("Parking duration by lot")
    plt.xlim(-0.5,)
    plt.tight_layout()
    plt.xticks(rotation=20)
    plt.savefig("static/lot_money.png")
    plt.close()
    return render_template('admin_summary.html')

@app.route('/dashboard/<int:id>/detailed',methods=["GET","POST"])
def detailed_view(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    conn=dbconn()
    cursor=conn.cursor()
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""select rs.user_id , rs.vehicle_no ,rs.parking_time, CASE 
                    when CAST((julianday(?) - julianday(parking_time)) * 24 AS INTEGER) < 1 THEN pl.price 
                    ELSE CAST((julianday(?) - julianday(parking_time)) * 24 AS INTEGER) * pl.price END as cost
                    from users u join reserve_spot rs 
                    on u.user_id=rs.user_id join parking_spot ps on ps.id=rs.spot_id join parking_lot pl on pl.id=ps.lot_id 
                    where rs.spot_id=? and rs.leave_time is null """,(now,now,id))
    data=cursor.fetchone()
    return render_template('detail_view.html', data=data ,id=id )