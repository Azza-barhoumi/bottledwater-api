from . import create_app, db
from .models import Brand, User

app = create_app()

BRANDS_FULL = [
    ("Safia_1","mineral","27/10/2020","SOSTEM","Ksour",250.0,25.0,7.0,20.0,0.6,140.0,15.0,10.0,3.0,0.2),
    ("Safia_2","mineral","24/03/2021","SOSTEM","Sra Ouertène",430.0,70.0,18.0,28.0,1.2,220.0,55.0,19.0,6.0,0.25),
    ("Sabrine","mineral","05/03/2021","SEEM","Chbika",320.0,45.0,12.0,36.0,2.0,150.0,20.0,40.0,10.0,0.6),
    ("Hayet","mineral","03/03/2021","S. Libre","Jelma",240.0,30.0,10.0,25.0,1.0,130.0,10.0,15.0,0.5,0.1),
    ("Jannet","mineral","16/03/2021","SEEM","Haffouz",245.0,32.0,9.0,22.0,0.5,110.0,15.0,12.0,1.0,0.2),
    ("Fourat","mineral","13/03/2021","SONEM","El Oueslatia",320.0,40.0,12.0,28.0,1.0,160.0,35.0,25.0,7.0,0.28),
    ("Cristaline","mineral","06/02/2021","SOSTEM","Zaghouan",720.0,131.0,37.0,100.0,3.0,357.0,249.0,127.0,32.0,1.4),
    ("Jektiss","table","09/10/2020","SBT","Koutine",260.0,25.0,9.0,22.0,0.6,135.0,20.0,60.0,2.0,0.12),
    ("Main","mineral","04/09/2016","SICEM","Foum Tataouine",300.0,50.0,10.0,30.0,1.0,180.0,40.0,30.0,8.0,0.22),
    ("Aqualine","mineral","01/12/2020","SMZ","Zaghouan",700.0,120.0,32.0,90.0,2.2,340.0,200.0,60.0,10.0,0.6),
    ("Mélina","mineral","14/01/2021","SIEM","Bargou",420.0,85.0,30.0,40.0,1.5,200.0,80.0,30.0,5.0,0.4),
    ("Primaqua","table","02/03/2021","SBT","Sidi Makhlouf",210.0,18.0,6.5,20.0,0.4,120.0,12.0,62.0,1.5,0.08),
    ("Saha","table","23/04/2021","LARK","El Fahs",220.0,16.0,5.0,18.0,0.45,125.0,9.0,70.0,2.0,0.07),
    ("Dima","mineral","09/03/2021","La Source","Tajrouine",310.0,33.0,11.0,26.0,0.9,170.0,30.0,21.1,0.2,0.2),
    ("Palma","mineral","23/04/2021","SOCEM","Sidi Iich",390.0,70.0,19.0,40.0,1.0,230.0,50.0,27.53,0.5,0.0),
    ("Melliti","mineral","26/02/2021","SOSTEM","Téboursouk",470.0,88.0,24.0,48.0,1.3,260.0,70.0,26.0,6.0,0.4),
    ("Royale","source","25/03/2021","ROYAL","Siliana",520.0,95.0,28.0,50.0,1.6,300.0,80.0,35.0,8.5,0.45),
    ("Bargou","source","12/05/2021","SEB.BA","Bargou",290.0,36.0,10.0,28.0,0.9,185.0,25.0,22.0,3.0,0.2),
    ("Denyna","source","02/03/2021","CHIFA","Hajeb El Ayoun",330.0,40.0,11.0,30.0,1.0,190.0,30.0,25.0,4.0,0.22),
    ("Vivian","source","18/01/2021","SOZEC","Zaghouan",360.0,45.0,13.0,32.0,1.1,200.0,35.0,126.0,2.9,0.28),
    ("Délice","source","03/04/2021","DÉLICE","Jelma",430.0,72.0,21.0,55.0,2.5,240.0,90.0,40.0,9.0,0.9),
    ("Tijen","mineral","16/03/2021","SIBAN","Jema",240.0,28.0,8.0,18.0,0.6,130.0,14.0,6.0,0.0,0.12),
    ("Beya","source","16/03/2021","SOTEM","Haffouz",315.0,44.0,10.0,26.0,0.9,175.0,22.0,18.0,4.0,0.21),
    ("Mira","source","23/02/2021","SGIA","Hajeb El Ayoun",300.0,38.0,11.0,27.0,0.9,180.0,26.0,20.0,2.0,0.2),
    ("Elixir","source","04/05/2021","RAYEN","Nefza",210.0,20.0,7.0,22.0,0.7,160.0,12.0,5.0,1.92,0.23),
    ("Pristine","mineral","30/12/2020","M.B.Turki","Zaghouan",600.0,110.0,30.0,85.0,2.0,320.0,180.0,55.0,12.0,0.55),
    ("May","source","25/03/2021","May TN","Le Krib",510.0,90.0,26.0,60.0,1.4,270.0,70.0,38.0,8.0,0.35),
]

def seed():
    with app.app_context():
        print("Dropping and recreating tables...")
        db.drop_all()
        db.create_all()

        # create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin')
            u.set_password('password')
            u.role = 'admin'
            db.session.add(u)

        print("Seeding brands...")
        for rec in BRANDS_FULL:
            name, typ, dmb, comp, region, ST, Ca, Mg, Na, K, HCO3, SO4, Cl, NO3, F = rec
            b = Brand(
                name=name,
                type=typ,
                dmb=dmb,
                company=comp,
                region=region,
                total_salts=float(ST),
                calcium=float(Ca),
                magnesium=float(Mg),
                sodium=float(Na),
                potassium=float(K),
                bicarbonates=float(HCO3),
                sulfates=float(SO4),
                chlorides=float(Cl),
                nitrates=float(NO3),
                fluorides=float(F)
            )
            db.session.add(b)

        db.session.commit()
        print("Seeded DB with brands and admin/password")

if __name__ == '__main__':
    seed()
