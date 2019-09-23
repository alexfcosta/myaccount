from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.defaultfilters import upper

from .forms import FindCustomerForm
from .models import Customers
import ibm_db, ibm_db_dbi


def home(request):
    if request.method == 'POST':
        form = FindCustomerForm(request.POST)
        if form.is_valid():
            surname = form.cleaned_data.get('surname')
            postcode = form.cleaned_data.get('postcode')
            messages.success(request, f'Search done for: {surname} @ {postcode}!')
            ibm_db_conn = ibm_db.connect("DATABASE=GCUKPRD;HOSTNAME=prddgcd001;PORT=50002;PROTOCOL=TCPIP;UID=costaa;PWD=London07;", "", "")
            conn = ibm_db_dbi.Connection(ibm_db_conn)
            cur = conn.cursor()
            #select = """
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
            and t1.PER_SURNAME = ?""", [upper(postcode), upper(surname)])
            #for c in Customers.objects.raw(select):
            #    print(c)

            #cur.execute(select, [upper(postcode), upper(surname)])
            #row = cur.fetchall()

            posts = []
            for obj in cur.fetchall():
                posts.append({"PER_GID": obj[0], "TITLE": obj[1], "INITIAL": obj[2], "FORENAME": obj[3], "SURNAME": obj[4], "STATUS": obj[5], "GENDER": obj[6], "CONTACT_TYPE": obj[7], "CONTACT_VALUE": obj[8], "POSTCODE": obj[9], "ADDRESS_LINE1": obj[10], "ADDRESS_LINE2": obj[11]})
            context = {'all_posts': cur.fetchall()}

            #print('sql results')
            print(posts)
            cur.close()
            conn.close()
            #ibm_db.close(ibm_db_conn)
            #return redirect('find-home')
            args = {'form': form, 'table': posts}
            return render(request, 'find/home.html', args)
    else:
        form = FindCustomerForm()
    #args = {'form': form, 'table': row}
    #return render(request, 'find/home.html', args)
    return render(request, 'find/home.html', {'form': form})


def about(request):
    return render(request, 'find/about.html', {'title': 'About'})
