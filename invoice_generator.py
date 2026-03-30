import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


dark_bg  = colors.HexColor('#0D1117')
card_bg  = colors.HexColor('#161B22')
border   = colors.HexColor('#30363D')
orange   = colors.HexColor('#E85D04')
gold     = colors.HexColor('#F9A825')
white    = colors.white
mid_gray = colors.HexColor('#8B949E')
lt_gray  = colors.HexColor('#CDD1D9')
green    = colors.HexColor('#238636')
yellow   = colors.HexColor('#E3B341')

# FIXED PATHS
QR_GPAY = "qr_codes/gpay_qr.JPG"
QR_PHONEPE = "qr_codes/phonepe_qr.PNG"

UPI_ID = "gaurav185@fam"

LOGO_PATH = "boris_logo.jpeg"


def ps(size=10, color=white, bold=False, align=TA_LEFT):
    return ParagraphStyle(
        'x',
        fontSize=size,
        textColor=color,
        fontName='Helvetica-Bold' if bold else 'Helvetica',
        alignment=align,
        leading=size+4,
        spaceAfter=2
    )


def dark_canvas(c, doc):
    c.saveState()
    c.setFillColor(dark_bg)
    c.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    c.restoreState()


def generate_invoice(name, customer_id, item, amount, paid='pending',
                     delivery_date='Pending', delivery_time='Pending', image_path=None):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    story = []

    invoice_date = datetime.date.today().strftime("%B %d, %Y")
    invoice_num  = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{str(customer_id)[-4:]}"
    is_paid = (paid == 'paid')


    # HEADER

    try:
        logo = Image(LOGO_PATH, width=1.5*inch, height=1.5*inch)
    except:
        logo = Paragraph("BORIS OG STORE", ps(14, gold, True))

    logo_block = Table([
        [logo, Table([
            [Paragraph("BORIS OG STORE", ps(20, white, True))],
            [Paragraph("BGMI SHOP", ps(9, gold, True))],
            [Paragraph("In-Game Account & Item Sales", ps(8, mid_gray))]
        ], colWidths=[2.8*inch])]
    ], colWidths=[1.6*inch, 2.9*inch])

    logo_block.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),dark_bg),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))


    status_text = "<font color='#238636'>● PAID IN FULL</font>" if is_paid else "<font color='#E3B341'>● PAYMENT PENDING</font>"

    invoice_block = Table([
        [Paragraph("INVOICE", ps(30, orange, True, TA_RIGHT))],
        [Paragraph(f"#{invoice_num}", ps(9, mid_gray, align=TA_RIGHT))],
        [Spacer(1,5)],
        [Paragraph(f"Date: {invoice_date}", ps(9, lt_gray, align=TA_RIGHT))],
        [Paragraph(f"Status: {status_text}", ps(9, lt_gray, align=TA_RIGHT))]
    ], colWidths=[3.3*inch])

    header = Table([[logo_block, invoice_block]], colWidths=[4.7*inch, 3.3*inch])

    story.append(header)
    story.append(HRFlowable(width="100%", thickness=2.5, color=gold, spaceAfter=12))


    # IMAGE SECTION

    if image_path:
        try:
            car = Image(image_path, width=7.4*inch, height=3.0*inch)
            car.hAlign = 'CENTER'

            ct = Table([[car]], colWidths=[7.5*inch])

            ct.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),card_bg),
                ('BOX',(0,0),(-1,-1),1,border)
            ]))

            story.append(ct)
            story.append(Spacer(1,12))

        except:
            pass


    # CUSTOMER INFO

    del_color = '#238636' if is_paid else '#E3B341'
    balance_text = "RS 0" if is_paid else f"RS {amount}"

    info = Table([
        ["BILL TO","ITEM DETAILS","PAYMENT"],
        [name,item,"Full Payment" if is_paid else "Pending"],
        ["Customer ID",customer_id,"Amount"],
        ["", "", f"RS {amount}"]
    ])

    story.append(info)
    story.append(Spacer(1,10))


    # LINE ITEMS

    items_rows = [
        ["DESCRIPTION","QTY","UNIT PRICE","TOTAL"],
        [item,"1",f"RS {amount}",f"RS {amount}"]
    ]

    lt = Table(items_rows, colWidths=[3.8*inch,0.6*inch,1.5*inch,1.5*inch])

    story.append(lt)
    story.append(Spacer(1,10))


    # TOTALS

    received = f"(RS {amount})" if is_paid else "RS 0"

    totals = Table([
        ["Total",f"RS {amount}"],
        ["Amount Received",received],
        ["Balance Due",balance_text]
    ], colWidths=[5.5*inch,2*inch])

    story.append(totals)
    story.append(Spacer(1,12))


    # PAYMENT QR SECTION

    try:

        gpay = Image(QR_GPAY, width=1.6*inch, height=1.6*inch)
        phonepe = Image(QR_PHONEPE, width=1.6*inch, height=1.6*inch)

        pay_title = Paragraph("SCAN TO PAY (UPI)", ps(11, gold, True, TA_CENTER))
        upi_text = Paragraph(f"UPI ID: {UPI_ID}", ps(10, lt_gray, True, TA_CENTER))

        qr_table = Table([
            [pay_title],
            [Table([[gpay, phonepe]], colWidths=[3.5*inch,3.5*inch])],
            [upi_text]
        ], colWidths=[7.5*inch])

        qr_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),card_bg),
            ('ALIGN',(0,1),(-1,1),'CENTER'),
            ('BOX',(0,0),(-1,-1),1,border)
        ]))

        story.append(qr_table)
        story.append(Spacer(1,12))

    except:
        pass


    # FOOTER

    ft = Table([[
        Paragraph("BORIS OG STORE — BGMI SHOP", ps(9,mid_gray,True)),
        Paragraph(
            f"Invoice issued on {invoice_date} | {'Payment received. Thank you!' if is_paid else 'Awaiting payment confirmation.'}",
            ps(9,mid_gray,align=TA_RIGHT)
        )
    ]], colWidths=[3.75*inch,3.75*inch])

    story.append(ft)


    doc.build(story, onFirstPage=dark_canvas, onLaterPages=dark_canvas)

    buffer.seek(0)

    return buffer.read()