from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.defaultfilters import upper

from .forms import Register1, Register2, Dashboard
import ibm_db, ibm_db_dbi


def home(request):
    if request.method == 'POST':
        form = Register1(request.POST)
        if form.is_valid():
            forename = form.cleaned_data.get('forename')
            surname = form.cleaned_data.get('surname')
            postcode = form.cleaned_data.get('postcode')
            email = form.cleaned_data.get('email')

            #request.session['_cust'] = form

            # DB2 Connection
            ibm_db_conn = ibm_db.connect("DATABASE=GCUKPRD;HOSTNAME=prddgcd001;PORT=50002;PROTOCOL=TCPIP;UID=costaa;PWD=London07;", "", "")
            conn = ibm_db_dbi.Connection(ibm_db_conn)

            cur = conn.cursor()
            # count the number of customers that match surname and postcode
            cur.execute("""
            select distinct t1.PER_GID
            from OPGCUK.PERSON_OPGC t1
            join OPGCUK.PERSON_CONTACT_POINT_ADDR_OPGC t2 on t1.PER_GID = t2.PER_GID
            where t2.PER_POSTAL_ADDR_POSTCODE = ?
            and t1.PER_SURNAME = ?
            and t1.PER_FIRST_INITIAL = ?""", [upper(postcode), upper(surname), upper(forename[0])])

            gid = []
            for obj in cur.fetchall():
                gid.append({"PER_GID": obj[0]})
            gid_num = len(gid)

            # DB2 Connection CLOSE
            cur.close()
            conn.close()

            if gid_num == 0:
                messages.warning(request, f'No customers in the database with the information provided.')
            elif gid_num == 1:
                messages.success(request, f'Customer {forename} {surname} @ {postcode} was found.')
                # phone = ''
                return redirect('find-dashboard', gid, forename, surname, postcode, email)
            else:
                # messages.warning(request, f'Please enter additional details required for your identification.')
                return redirect('find-register2', forename, surname, postcode, email)
    else:
        form = Register1()
    #args = {'form': form, 'table': row}
    #return render(request, 'find/home.html', args)
    return render(request, 'find/home.html', {'form': form})


def register2(request, forename, surname, postcode, email):

    # DB2 Connection
    ibm_db_conn = ibm_db.connect(
        "DATABASE=GCUKPRD;HOSTNAME=prddgcd001;PORT=50002;PROTOCOL=TCPIP;UID=costaa;PWD=London07;", "", "")
    conn = ibm_db_dbi.Connection(ibm_db_conn)
    cur = conn.cursor()

    cur.execute("""
    select distinct t1.PER_GID, t1.PER_TITLE_CODE as TITLE, t1.PER_FIRST_INITIAL as INITIAL, t1.PER_FORENAME as FORENAME, t1.PER_SURNAME as SURNAME, t1.PER_STATUS_CODE as STATUS,
        CASE t1.PER_GENDER_CODE
        WHEN '1' THEN 'MALE'
        WHEN '2' THEN 'FEMALE'
        ELSE 'Other'
        END as GENDER,
        t3.PER_CP_CAT_CODE as CONTACT_TYPE, t3.PER_CP_VALUE as CONTACT_VALUE, t2.PER_POSTAL_ADDR_POSTCODE as POSTCODE, t2.PER_POSTAL_ADDR_LINE_1 as ADDRESS_LINE1, t2.PER_POSTAL_ADDR_LINE_2 as ADDRESS_LINE2
    from OPGCUK.PERSON_OPGC t1
    join OPGCUK.PERSON_CONTACT_POINT_ADDR_OPGC t2 on t1.PER_GID = t2.PER_GID
    join OPGCUK.PERSON_CONTACT_POINT_OPGC t3 on t3.PER_GID = t1.PER_GID
    where t2.PER_POSTAL_ADDR_POSTCODE = ?
    and t1.PER_SURNAME = ?
    and t1.PER_FIRST_INITIAL = ?""", [upper(postcode), upper(surname), upper(forename[0])])

    cust = []
    for obj in cur.fetchall():
        cust.append({"PER_GID": obj[0], "TITLE": obj[1], "INITIAL": obj[2], "FORENAME": obj[3], "SURNAME": obj[4],
                      "STATUS": obj[5], "GENDER": obj[6], "CONTACT_TYPE": obj[7], "CONTACT_VALUE": obj[8],
                      "POSTCODE": obj[9], "ADDRESS_LINE1": obj[10], "ADDRESS_LINE2": obj[11]})
    context = {'all_posts': cur.fetchall()}
    tab_len = len(cust)


    cur.execute("""
    select distinct t2.PER_GID, t4.ITEM_ID as PLAN
    from OPGCUK.PERSON_ITEM_RELATIONSHIP_OPGC t2
    join OPGCUK.ITEM_OPGC t3 on t3.ITEM_GID = t2.ITEM_GID and t2.ITEM_REL_CAT = 'OWN'
    join OPGCUK.ITEM_SOURCE_DETAIL_OPGC t4 on t4.ITEM_GID = t3.ITEM_GID
    join REFDATA_INT.REF_ITEM t5 on t3.ITEM_CODE = t5.ITEM_CODE and t5.COUNTRY_CODE = 'GBR'
    where left(t4.ITEM_ID,4) = 'PLN:'
    and t3.ITEM_COVER_DG_CONTR_STATUS_CODE in ('N','R','L') -- exclude Cancelled
    and t2.PER_GID IN (
    select distinct t1.PER_GID
            from OPGCUK.PERSON_OPGC t1
            join OPGCUK.PERSON_CONTACT_POINT_ADDR_OPGC t2 on t1.PER_GID = t2.PER_GID
            where t2.PER_POSTAL_ADDR_POSTCODE = ?
            and t1.PER_SURNAME = ?
            and t1.PER_FIRST_INITIAL = ?)""", [upper(postcode), upper(surname), upper(forename[0])])

    plans = []
    for obj in cur.fetchall():
        plans.append({"PER_GID": obj[0], "PLAN": obj[1]})

    # DB2 Connection CLOSE
    cur.close()
    conn.close()

    print(upper(email))

    c = cust.count(upper(email))

    try:
        i = cust.index(upper(email))
    except ValueError:
        index_value = -1

    print('count: ', c)
    print('index: ', c)

    if upper(email) in cust:
        print('found email: ',upper(email),' for GID = ')

    i = 0
    for row in cust:
        if row['CONTACT_VALUE'] == upper(email) or forename == row['FORENAME']:
            i+=1
            if i == 1:
                gid = row['PER_GID']
            elif gid != row['PER_GID']:
                messages.warning(request, f'Please enter additional details required for your identification.')

    if i == 1:
        print('Found one - GID :', gid)
        messages.success(request, f'Thank you {forename} {surname} your account was created.')
        phone = ''
        return redirect('find-dashboard', gid, forename, surname, postcode, email)
    else:
        messages.warning(request, f'Please enter additional details required for your identification.')
        form = Register2()
        # send data to form
        args = {'form': form, 'table': cust, 'tab_len': tab_len, 'plans': plans, 'forename': forename, 'surname': surname, 'postcode': postcode, 'email': email}
        return render(request, 'find/home.html', args)

        if request.method == 'POST':
            form = Register2(request.POST)
            if form.is_valid():
                phone = form.cleaned_data.get('phone')
                line1 = form.cleaned_data.get('line1')
                plan = form.cleaned_data.get('plan')


                # DB2 Connection
                ibm_db_conn = ibm_db.connect("DATABASE=GCUKPRD;HOSTNAME=prddgcd001;PORT=50002;PROTOCOL=TCPIP;UID=costaa;PWD=London07;", "", "")
                conn = ibm_db_dbi.Connection(ibm_db_conn)

    #            if gid_num == 0:
    #                messages.warning(request, f'No customers in the database with the information provided.')
    #            elif gid_num == 1:
    #                messages.success(request, f'Customer {forename} {surname} @ {postcode} was found.')
                    #form = Register2()
    #            else:
    #                messages.warning(request, f'Please enter additional details required for your identification.')


        else:
            form = Register2()

        return render(request, 'find/home.html', {'form': form})


def dashboard(request, gid, forename, surname, postcode, email):

    # DB2 Connection
    ibm_db_conn = ibm_db.connect(
        "DATABASE=GCUKPRD;HOSTNAME=prddgcd001;PORT=50002;PROTOCOL=TCPIP;UID=costaa;PWD=London07;", "", "")
    conn = ibm_db_dbi.Connection(ibm_db_conn)
    cur = conn.cursor()

    # retrieve all plans from customer
    cur.execute("""
    select distinct t2.PER_GID, t3.ITEM_GID, t4.ITEM_ID as PLAN, t3.ITEM_LOC_ADDR_LINE_1 as ITEM_LOCATION, t3.ITEM_LOC_POSTCODE AS POSTCODE, t3.ITEM_MANUF_BRAND_CODE AS BRAND, t3.ITEM_MODEL_NUM AS MODEL, t3.ITEM_SERIAL_NUM AS SERIAL, 
       date(t3.ITEM_PURCHASE_DTS) AS PURCHASE_DATE, date(t3.ITEM_COVER_DG_CONTR_RENEWAL_DTS) AS RENEWAL_DATE, 
       CASE t3.ITEM_COVER_DG_CONTR_STATUS_CODE
       WHEN 'N' THEN 'NEW'
       WHEN 'R' THEN 'RENEWED'
       WHEN 'L' THEN 'LAPSED'
       WHEN 'C' THEN 'CANCELLED'
       ELSE 'ERROR'
       END as PLAN_STATUS,
       t3.ITEM_CODE AS ITEM_CODE, t5.ITEM_DESCRIPTION AS DESCRIPTION, t5.ITEM_FAMILY_CODE AS FAMILY
    from OPGCUK.PERSON_ITEM_RELATIONSHIP_OPGC t2
    join OPGCUK.ITEM_OPGC t3 on t3.ITEM_GID = t2.ITEM_GID and t2.ITEM_REL_CAT = 'OWN'
    join OPGCUK.ITEM_SOURCE_DETAIL_OPGC t4 on t4.ITEM_GID = t3.ITEM_GID
    join REFDATA_INT.REF_ITEM t5 on t3.ITEM_CODE = t5.ITEM_CODE and t5.COUNTRY_CODE = 'GBR'
    where t2.PER_GID = ?
    and left(t4.ITEM_ID,4) = 'PLN:'
    and t3.ITEM_COVER_DG_CONTR_STATUS_CODE in ('N','R','L')""", [gid])

    plans = []
    for obj in cur.fetchall():
        plans.append({"PER_GID": obj[0], "ITEM_GID": obj[1], "PLAN": obj[2], "ITEM_LOCATION": obj[3], "POSTCODE": obj[4],
                      "BRAND": obj[5], "MODEL": obj[6], "SERIAL": obj[7], "PURCHASE_DATE": obj[8],
                      "RENEWAL_DATE": obj[9], "PLAN_STATUS": obj[10], "ITEM_CODE": obj[11], "DESCRIPTION": obj[12], "FAMILY": obj[13]})
    #context = {'all_posts': cur.fetchall()}
    tab_len = len(plans)

    # retrieve all mailers from customer
    cur.execute("""
    select distinct t2.PER_GID, t3.ITEM_GID, t3.ITEM_LOC_ADDR_LINE_1 as ITEM_LOCATION, t3.ITEM_LOC_POSTCODE AS POSTCODE, 
        t3.ITEM_MANUF_BRAND_CODE AS BRAND, t3.ITEM_MODEL_NUM AS MODEL, t3.ITEM_SERIAL_NUM AS SERIAL, 
        date(t3.ITEM_PURCHASE_DTS) AS PURCHASE_DATE,
        t3.ITEM_CODE AS ITEM_CODE, t5.ITEM_DESCRIPTION AS DESCRIPTION, t5.ITEM_FAMILY_CODE AS FAMILY
    from OPGCUK.PERSON_ITEM_RELATIONSHIP_OPGC t2
    join OPGCUK.ITEM_OPGC t3 on t3.ITEM_GID = t2.ITEM_GID and t2.ITEM_REL_CAT = 'OWN'
    join OPGCUK.ITEM_SOURCE_DETAIL_OPGC t4 on t4.ITEM_GID = t3.ITEM_GID
    join REFDATA_INT.REF_ITEM t5 on t3.ITEM_CODE = t5.ITEM_CODE and t5.COUNTRY_CODE = 'GBR'
    where t2.PER_GID = ?
    and left(t4.ITEM_ID,4) <> 'PLN:'
    and t3.ITEM_COVER_DG_CONTR_STATUS_CODE is NULL""", [gid])

    mailers = []
    for obj in cur.fetchall():
        mailers.append({"PER_GID": obj[0], "ITEM_GID": obj[1], "ITEM_LOCATION": obj[2], "POSTCODE": obj[3],
                      "BRAND": obj[4], "MODEL": obj[5], "SERIAL": obj[6], "PURCHASE_DATE": obj[7],
                      "ITEM_CODE": obj[8], "DESCRIPTION": obj[9], "FAMILY": obj[10]})
    #context = {'all_posts': cur.fetchall()}
    tab_len = tab_len + len(mailers)

    # DB2 Connection CLOSE
    cur.close()
    conn.close()

    form = Dashboard(initial={'gid': gid, 'forename': forename, 'surname': surname, 'postcode': postcode, 'email': email})
    # send data to form
    args = {'form': form, 'plans': plans, 'mailers': mailers, 'item_len': tab_len}
    return render(request, 'find/dashboard.html', args)


def about(request):
    return render(request, 'find/about.html', {'title': 'About'})
