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
    invoice_num = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{str(customer_id)[-4:]}"
    is_paid = paid.lower() == "paid"


    # HEADER -------------------------------------------------

    try:
        logo = Image(LOGO_PATH, width=1.5*inch, height=1.5*inch)
    except:
        logo = Paragraph("BORIS OG STORE", ps(16, gold, True))

    left_header = Table([
        [logo,
         Paragraph(
             "<b>BORIS OG STORE</b><br/><font color='#F9A825'>BGMI SHOP</font><br/>"
             "<font size=8 color='#8B949E'>In-Game Account & Item Sales</font>",
             ps(14, white, True)
         )]
    ], colWidths=[1.6*inch,3.0*inch])


    status_text = "● PAID IN FULL" if is_paid else "● PAYMENT PENDING"

    right_header = Table([
        [Paragraph("INVOICE", ps(30, orange, True, TA_RIGHT))],
        [Paragraph(f"#{invoice_num}", ps(10, mid_gray, align=TA_RIGHT))],
        [Paragraph(f"Date: {invoice_date}", ps(10, lt_gray, align=TA_RIGHT))],
        [Paragraph(status_text, ps(10, green if is_paid else yellow, True, TA_RIGHT))]
    ], colWidths=[3.3*inch])

    header = Table([[left_header, right_header]], colWidths=[4.5*inch,3.0*inch])

    story.append(header)
    story.append(HRFlowable(width="100%", thickness=2.5, color=gold))
    story.append(Spacer(1,12))


    # PRODUCT IMAGE ------------------------------------------

    if image_path:
        try:
            img = Image(image_path, width=7.2*inch, height=3*inch)
            img.hAlign = 'CENTER'

            img_box = Table([[img]])
            img_box.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),card_bg),
                ('BOX',(0,0),(-1,-1),1,border)
            ]))

            story.append(img_box)
            story.append(Spacer(1,12))

        except:
            pass


    # BILL / ITEM / PAYMENT ----------------------------------

    balance = "RS 0" if is_paid else f"RS {amount}"

    info_table = Table([
        ["BILL TO","ITEM DETAILS","PAYMENT"],

        [Paragraph(f"<b>{name}</b>",ps(12,white,True)),
         Paragraph(f"<b>{item}</b>",ps(12,white,True)),
         Paragraph("Method: Full Payment" if is_paid else "Method: Pending",
                   ps(11,green if is_paid else yellow,True))],

        [Paragraph("Customer ID:",ps(9,mid_gray)),
         Paragraph("Type: In-Game Account",ps(10,lt_gray)),
         Paragraph("Amount Due:",ps(9,mid_gray))],

        [Paragraph(str(customer_id),ps(11,white,True)),
         Paragraph("Platform: BGMI / Game Store",ps(10,lt_gray)),
         Paragraph(f"RS {amount}",ps(12,gold,True))],

        ["",
         Paragraph(f"<b>Delivery Date:</b> {delivery_date}",ps(10,white)),
         Paragraph("● PAID" if is_paid else "● NOT RECEIVED",
                   ps(11,green if is_paid else colors.red,True))],

        ["",
         Paragraph(f"<b>Delivery Time:</b> {delivery_time}",ps(10,white)),
         Paragraph(f"Balance: {balance}",
                   ps(11,green if is_paid else colors.red,True))]
    ], colWidths=[2.4*inch,3.1*inch,2.0*inch])

    info_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),card_bg),
        ('BOX',(0,0),(-1,-1),1,border),
        ('LINEBELOW',(0,0),(-1,0),1,gold)
    ]))

    story.append(info_table)
    story.append(Spacer(1,12))


    # LINE ITEMS ----------------------------------------------

    items = Table([
        ["DESCRIPTION","QTY","UNIT PRICE","TOTAL"],
        [item,"1",f"RS {amount}",f"RS {amount}"]
    ], colWidths=[3.8*inch,0.6*inch,1.5*inch,1.5*inch])

    items.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),dark_bg),
        ('BACKGROUND',(0,1),(-1,-1),card_bg),
        ('LINEBELOW',(0,0),(-1,0),1,gold),
        ('BOX',(0,0),(-1,-1),1,border)
    ]))

    story.append(items)
    story.append(Spacer(1,10))


    # TOTALS --------------------------------------------------

    totals = Table([
        ["Total",f"RS {amount}"],
        ["Amount Received",f"RS {amount}" if is_paid else "RS 0"],
        ["BALANCE DUE",balance]
    ], colWidths=[5.5*inch,2*inch])

    totals.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),card_bg),
        ('BACKGROUND',(0,2),(-1,2),colors.HexColor('#1C1407')),
        ('BOX',(0,0),(-1,-1),1,border)
    ]))

    story.append(totals)
    story.append(Spacer(1,12))


    # PAYMENT QR ----------------------------------------------

    try:

        gpay = Image(QR_GPAY, width=1.6*inch, height=1.6*inch)
        phonepe = Image(QR_PHONEPE, width=1.6*inch, height=1.6*inch)

        qr_section = Table([
            [Paragraph("SCAN TO PAY (UPI)",ps(11,gold,True,TA_CENTER))],
            [Table([[gpay,phonepe]],colWidths=[3.5*inch,3.5*inch])],
            [Paragraph(f"UPI ID: {UPI_ID}",ps(10,lt_gray,True,TA_CENTER))]
        ])

        qr_section.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),card_bg),
            ('BOX',(0,0),(-1,-1),1,border)
        ]))

        story.append(qr_section)

    except:
        pass


    # FOOTER --------------------------------------------------

    footer = Table([[
        Paragraph("BORIS OG STORE — BGMI SHOP",ps(9,mid_gray,True)),
        Paragraph(f"Invoice issued on {invoice_date}",ps(9,mid_gray,align=TA_RIGHT))
    ]], colWidths=[3.75*inch,3.75*inch])

    story.append(Spacer(1,15))
    story.append(footer)


    doc.build(story,onFirstPage=dark_canvas,onLaterPages=dark_canvas)

    buffer.seek(0)
    return buffer.read()