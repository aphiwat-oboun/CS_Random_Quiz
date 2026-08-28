# -*- coding: utf-8 -*-
"""
Script to generate the complete 350-question seed_data.py command file
including 150 existing questions + 200 new challenging/tricky questions (Medium to Hard level)
with automated choice shuffling (A, B, C, D) and syncing to SQLite & Firebase.
"""
import os
import json

# Let's define the 200 new questions in detail
new_200_questions = [
    # -------------------------------------------------------------
    # Category 1: Computer Hardware, Architecture, Microcontrollers (35 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ในกระบวนการประมวลผลคำสั่งของ CPU ขั้นตอนใดทำหน้าที่แปลงรหัส Machine Code เป็นสัญญาณควบคุม?",
        "correct": "Decode (ถอดรหัสคำสั่ง)", "distractors": ["Fetch (ดึงคำสั่ง)", "Execute (ประมวลผล)", "Write-back (เขียนกลับ)"],
        "explanation": "กระบวนการ Instruction Cycle เริ่มจาก Fetch -> Decode (แปลรหัส) -> Execute -> Write-back"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "การจัดเก็บข้อมูลในหน่วยความจำแบบ 'Little Endian' มีลักษณะการเรียงไบต์อย่างไร?",
        "correct": "เก็บไบต์ที่มีค่าน้อยที่สุด (LSB) ไว้ที่ Address ต่ำสุด", "distractors": ["เก็บไบต์ที่มีค่ามากที่สุด (MSB) ไว้ที่ Address ต่ำสุด", "เก็บเฉพาะเลขคู่ไว้ก่อนเลขคี่", "เรียงลำดับตามตัวอักษร A-Z"],
        "explanation": "Little Endian (เช่น สถาปัตยกรรม x86) เก็บ Least Significant Byte ไว้ที่ต่ำสุด ตรงข้ามกับ Big Endian"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ชิปแรมประเภท 'ECC RAM' แตกต่างจากแรมทั่วไปในเครื่องคอมพิวเตอร์ตามบ้านอย่างไร?",
        "correct": "มีวงจรตรวจจับและแก้ไขข้อผิดพลาดของบิตข้อมูลอัตโนมัติ", "distractors": ["มีความเร็วบัสสูงกว่าแรมปกติ 10 เท่า", "กินไฟน้อยกว่าแรมทั่วไป 80%", "สามารถทำงานได้โดยไม่ต้องใช้ชิปเซต"],
        "explanation": "ECC (Error-Correcting Code) RAM นิยมใช้ใน Server เพื่อป้องกันข้อมูลเสียหายจาก Single-bit Error"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "หน่วยวัด 'IOPS' ในการทดสอบประสิทธิภาพของ SSD หรือฮาร์ดดิสก์ ย่อมาจากอะไร?",
        "correct": "Input/Output Operations Per Second", "distractors": ["Internal Operating Power Supply", "Integrated Output Processing Speed", "Internet Online Protocol Standard"],
        "explanation": "IOPS วัดจำนวนครั้งที่อุปกรณ์จัดเก็บสามารถอ่านหรือเขียนไฟล์สุ่มขนาดเล็กต่อหนึ่งวินาที"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ประเภทของชิปหน่วยความจำแฟลช (NAND Flash) ข้อใดมีอายุการใช้งานและจำนวนรอบการเขียน (Endurance) ทนทานที่สุด?",
        "correct": "SLC (Single-Level Cell)", "distractors": ["MLC (Multi-Level Cell)", "TLC (Triple-Level Cell)", "QLC (Quad-Level Cell)"],
        "explanation": "SLC เก็บ 1 บิตต่อเซลล์ จึงมีความเร็ว ทนทาน และราคาสูงที่สุดเมื่อเทียบกับ MLC, TLC และ QLC"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "พอร์ตเชื่อมต่อหน้าจอแบบ 'DisplayPort' มีความสามารถพิเศษใดที่ HDMI ทั่วไปทำไม่ได้?",
        "correct": "Daisy Chaining ต่อจอมอนิเตอร์หลายจอเรียงกันจากพอร์ตเดียว", "distractors": ["ส่งกระแสไฟฟ้า 220V เข้าจอได้", "เปลี่ยนคอมพิวเตอร์เป็นเซิร์ฟเวอร์", "รับสัญญาณวิทยุ FM"],
        "explanation": "DisplayPort รองรับเทคโนโลยี MST (Multi-Stream Transport) สามารถต่อสายพ่วงจอภาพตัวที่สองจากจอตัวแรกได้"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "วงจร 'VRM' (Voltage Regulator Module) บนเมนบอร์ดมีหน้าที่สำคัญที่สุดคืออะไร?",
        "correct": "แปลงและควบคุมแรงดันไฟบ้านให้เสถียรสำหรับจ่ายให้ CPU/GPU", "distractors": ["แปลงสัญญาณภาพเป็นสัญญาณเสียง", "เพิ่มความเร็วสัญญาณอินเทอร์เน็ต", "ควบคุมความเร็วพัดลมเคส"],
        "explanation": "VRM แปลงไฟ 12V จาก PSU ให้ลดลงเหลือแรงดันแม่นยำประมาณ 1.0-1.4V เพื่อจ่ายไฟให้ CPU อย่างนิ่งที่สุด"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "ค่า 'IPC' (Instructions Per Cycle) ของ CPU บ่งชี้ถึงสิ่งใด?",
        "correct": "จำนวนคำสั่งเฉลี่ยที่ประมวลผลได้สำเร็จใน 1 รอบสัญญาณนาฬิกา", "distractors": ["จำนวนคอร์ทั้งหมดที่อยู่ในชิป", "อุณหภูมิความร้อนสูงสุดที่ทนได้", "ขนาดหน่วยความจำแคชรวม"],
        "explanation": "ประสิทธิภาพ CPU เท่ากับ Clock Speed x IPC แม้ความเร็วสัญญาณนาฬิกาเท่ากันแต่ถ้า IPC สูงกว่าจะทำงานเร็วกว่า"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "บนบอร์ดไมโครคอนโทรลเลอร์ สัญญาณแบบ 'PWM' (Pulse Width Modulation) นิยมนำไปใช้ทำอะไร?",
        "correct": "หรี่ความสว่างหลอด LED หรือคุมความเร็วมอเตอร์", "distractors": ["ต่อสายแลนเข้าอินเทอร์เน็ต", "แปลงไฟล์เพลงเป็น MP3", "ล้างโปรแกรมในชิปทิ้ง"],
        "explanation": "PWM คือการเปิด-ปิดสัญญาณดิจิทัลเป็นจังหวะถี่ ๆ เพื่อจำลองแรงดันแอนะล็อก เช่น หรี่ไฟ LED หรือเร่งมอเตอร์"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "โปรโตคอลสื่อสารแบบ 'I2C' (I-Squared-C) ใช้สายสัญญาณหลักในการรับส่งข้อมูลกี่เส้น?",
        "correct": "2 เส้น (SDA สำหรับข้อมูล และ SCL สำหรับสัญญาณนาฬิกา)", "distractors": ["1 เส้น (สัญญาณเดี่ยว)", "4 เส้น (MISO, MOSI, SCK, CS)", "8 เส้น (แบบขนาน 8 บิต)"],
        "explanation": "I2C สื่อสารแบบอนุกรมใช้สายเพียง 2 เส้นคือ SDA (Serial Data) และ SCL (Serial Clock)"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "โปรโตคอลสื่อสารอนุกรมแบบ 'SPI' (Serial Peripheral Interface) ใช้สายสัญญาณใดในการเลือกอุปกรณ์ปลายทาง?",
        "correct": "SS / CS (Slave Select / Chip Select)", "distractors": ["MOSI", "MISO", "SCLK"],
        "explanation": "SPI ใช้สาย CS (Chip Select) ควบคุมการเปิดใช้งานอุปกรณ์เป้าหมายที่ต้องการรับส่งข้อมูลด้วย"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "บอร์ด 'Raspberry Pi' แตกต่างจาก 'Arduino Uno' ในสาระสำคัญอย่างไร?",
        "correct": "Raspberry Pi เป็นคอมพิวเตอร์บอร์ดเดี่ยว (SBC) มี OS ในขณะที่ Arduino เป็นไมโครคอนโทรลเลอร์", "distractors": ["Raspberry Pi ใช้งานได้เฉพาะกับหน้าจอทีวี", "Arduino มีชิปประมวลผลเร็วกว่า 100 เท่า", "ทั้งคู่คือสิ่งเดียวกันแต่คนละยี่ห้อ"],
        "explanation": "Raspberry Pi เป็น Single Board Computer รัน Linux ได้ ส่วน Arduino เป็น Microcontroller รันโค้ดฝังตัวลูปเดียว"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "หน้าจอมอนิเตอร์พาเนลชนิด 'OLED' มีจุดเด่นเหนือพาเนล 'IPS' ในเรื่องใดชัดเจนที่สุด?",
        "correct": "แสดงสีดำได้สนิท 100% เพราะแต่ละพิกเซลกำเนิดแสงได้เอง", "distractors": ["ประหยัดไฟที่สุดเมื่อเปิดภาพสีขาวล้วน", "มีราคาถูกกว่าพาเนลทุกชนิด", "ไม่เสี่ยงต่อปัญหาหน้าจอเบิร์นอิน"],
        "explanation": "OLED แต่ละเม็ดพิกเซลสามารถดับไฟได้สนิท ทำให้ได้ค่า Contrast Ratio แบบ Infinite และสีดำลึกสมบูรณ์แบบ"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "ค่า 'Baud Rate' ในการสื่อสารข้อมูลทางพอร์ตอนุกรม (Serial Port) หมายถึงอะไร?",
        "correct": "ความเร็วในการส่งสัญญาณหรือการเปลี่ยนสถานะต่อวินาที", "distractors": ["ระยะห่างของสายไฟที่ส่งได้ไกลสุด", "จำนวนอุปกรณ์สูงสุดที่ต่อพ่วงได้", "ปริมาณไฟฟ้าที่ใช้ขับเคลื่อน"],
        "explanation": "Baud Rate คืออัตราความเร็วการส่งสัญญาณทางอนุกรม เช่น 9600 หรือ 115200 Baud"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "สถาปัตยกรรมแบบ 'von Neumann' มีข้อจำกัดที่เรียกว่า 'von Neumann Bottleneck' จากสาเหตุใด?",
        "correct": "CPU และหน่วยความจำต้องแชร์บัสส่งข้อมูลและคำสั่งร่วมกัน", "distractors": ["ไม่อนุญาตให้ใช้เลขฐานสอง", "ไม่สามารถใส่การ์ดจอแยกได้", "ต้องใช้คีย์บอร์ดแบบโบราณเท่านั้น"],
        "explanation": "von Neumann แชร์ Bus เดียวกันระหว่างข้อมูลและคำสั่ง ทำให้ความเร็วระบบถูกจำกัดที่ความเร็ว Bus เชื่อมต่อ"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "สถาปัตยกรรมคอมพิวเตอร์แบบ 'Harvard Architecture' แก้ปัญหาบัสคอขวดอย่างไร?",
        "correct": "แยกบัสและหน่วยความจำของคำสั่ง (Code) กับข้อมูล (Data) ออกจากกัน", "distractors": ["ใช้ชิป CPU สองตัวประมวลผลพร้อมกัน", "เพิ่มขนาดแรมให้ไม่จำกัด", "ยกเลิกการใช้ระบบปฏิบัติการ"],
        "explanation": "Harvard Architecture แยก Memory และ Bus สำหรับ Instruction และ Data ทำให้เข้าถึงพร้อมกันได้ในรอบสัญญาณเดียว"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "สาเหตุของ 'Cache Miss' ประเภท 'Compulsory Miss' (หรือ Cold Miss) เกิดจากอะไร?",
        "correct": "เป็นการเรียกใช้ข้อมูลบล็อกนั้นเป็นครั้งแรกในระบบ", "distractors": ["ขนาดของ Cache เล็กเกินไปจนจุไม่พอ", "เกิดการชนกันของตำแหน่ง Mapping", "ชิป Cache ร้อนเกินกำหนด"],
        "explanation": "Compulsory Miss เกิดเมื่อโปรแกรมเพิ่งเริ่มทำงานและเรียกบล็อกข้อมูลนั้นเป็นครั้งแรก จึงต้องโหลดจาก RAM เสมอ"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "อุปกรณ์ 'ADC' (Analog-to-Digital Converter) ในวงจรอิเล็กทรอนิกส์ทำหน้าที่อะไร?",
        "correct": "แปลงสัญญาณแอนะล็อกต่อเนื่องให้เป็นตัวเลขดิจิทัล", "distractors": ["แปลงไฟกระแสตรงเป็นไฟกระแสสลับ", "เพิ่มความดังของเสียงลำโพง", "แปลงรหัสผ่านเป็นตัวเลข"],
        "explanation": "ADC อ่านค่าแรงดันแอนะล็อกต่อเนื่อง (เช่น จากเซนเซอร์วัดอุณหภูมิ) ให้กลายเป็นค่าตัวเลขดิจิทัลให้ไมโครคอนโทรลเลอร์อ่านได้"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ข้อกำหนด PCIe Gen 4.0 ส่งข้อมูลได้ความเร็วสูงสุดประมาณเท่าใดต่อ 1 Lane (x1)?",
        "correct": "ประมาณ 2 GB/s (16 GT/s)", "distractors": ["ประมาณ 500 MB/s", "ประมาณ 10 GB/s", "ประมาณ 100 MB/s"],
        "explanation": "PCIe 4.0 ทำความเร็ว ~2 GB/s ต่อ 1 Lane ดังนั้นสล็อต x16 จึงทำความเร็วได้สูงถึง ~32 GB/s (สองทิศทาง 64 GB/s)"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "เทคโนโลยีจอภาพ 'FreeSync' หรือ 'G-Sync' มีไว้เพื่อแก้ปัญหาภาพแบบใดเวลาเล่นเกม?",
        "correct": "อาการภาพฉีกขาด (Screen Tearing)", "distractors": ["อาการจอภาพดับมืดสนิท", "อาการสีเพี้ยนเป็นขาวดำ", "อาการเสียงดีเลย์ไม่ตรงกับภาพ"],
        "explanation": "Adaptive Sync ปรับ Refresh Rate ของจอให้ตรงกับ Frame Rate ของการ์ดจอ ป้องกันภาพขาดแหว่ง (Tearing)"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ในระบบเครือข่าย ค่า 'MTU' (Maximum Transmission Unit) ค่าเริ่มต้นของอีเทอร์เน็ตมาตรฐานมีขนาดเท่าใด?",
        "correct": "1,500 ไบต์", "distractors": ["64 ไบต์", "512 ไบต์", "9,000 ไบต์"],
        "explanation": "Standard Ethernet Frame กำหนดค่า MTU สูงสุดสำหรับ Payload ข้อมูลไว้ที่ 1,500 Bytes"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "สายเคเบิลคู่บิดเกลียวแบบ 'Cat 6' รองรับความเร็วเครือข่าย 10 Gbps ได้ระยะทางไกลสูงสุดประมาณกี่เมตร?",
        "correct": "ประมาณ 55 เมตร", "distractors": ["100 เมตรเต็ม", "10 เมตร", "1 กิโลเมตร"],
        "explanation": "Cat 6 รองรับ 10 Gbps ที่ระยะไม่เกิน 55 เมตร (ถ้าต้องการ 100 เมตรเต็มที่ 10 Gbps ต้องใช้สาย Cat 6A ขึ้นไป)"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "ฮาร์ดแวร์ 'PoE' (Power over Ethernet) มีประโยชน์อย่างไรในการติดตั้งกล้องวงจรปิด?",
        "correct": "จ่ายกระแสไฟเลี้ยงอุปกรณ์ผ่านสายแลนเส้นเดียวกับข้อมูล", "distractors": ["เพิ่มความเร็วเน็ตเป็น 100 เท่า", "ทำให้กล้องถ่ายภาพในที่มืดได้", "ป้องกันกล้องถูกขโมย"],
        "explanation": "PoE ส่งทั้งไฟฟ้าและสัญญาณข้อมูลผ่านสายเคเบิลอีเทอร์เน็ตเส้นเดียว จึงไม่ต้องเดินสายไฟแยกให้กล้องหรือ Access Point"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "หัวต่อสายไฟเลี้ยงการ์ดจอรุ่นใหม่ '12VHPWR' (PCIe 5.0 16-pin) สามารถจ่ายไฟได้สูงสุดกี่วัตต์?",
        "correct": "600 วัตต์", "distractors": ["150 วัตต์", "300 วัตต์", "1,200 วัตต์"],
        "explanation": "มาตรฐาน 12VHPWR 16-pin ออกแบบมาเพื่อจ่ายพลังงานได้สูงสุดถึง 600W ผ่านสายเส้นเดียวสำหรับการ์ดจอระดับท็อป"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "มาตรฐานการเชื่อมต่อไร้สาย 'Wi-Fi 6' ทำงานบนมาตรฐาน IEEE รหัสใด?",
        "correct": "IEEE 802.11ax", "distractors": ["IEEE 802.11ac", "IEEE 802.11n", "IEEE 802.3"],
        "explanation": "Wi-Fi 4 = 802.11n, Wi-Fi 5 = 802.11ac, Wi-Fi 6/6E = 802.11ax, Wi-Fi 7 = 802.11be"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ชิปเซตบริดจ์ในเมนบอร์ดแบบดั้งเดิม 'Southbridge' ทำหน้าที่ควบคุมอุปกรณ์กลุ่มใด?",
        "correct": "พอร์ต I/O, USB, SATA, เสียง และบัสความเร็วต่ำ", "distractors": ["CPU และ แรมความเร็วสูง", "เฉพาะการ์ดจอ PCIe x16 เท่านั้น", "ควบคุมไฟบ้านก่อนเข้าเคส"],
        "explanation": "Northbridge คุม CPU, RAM, การ์ดจอความเร็วสูง ส่วน Southbridge คุมพอร์ตเชื่อมต่อ I/O และสตอเรจความเร็วต่ำ"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "เทคโนโลยี 'DirectX' หรือ 'Vulkan' จัดเป็นซอฟต์แวร์ประเภทใดในระบบคอมพิวเตอร์?",
        "correct": "Graphics API สำหรับให้เกมติดต่อกับการ์ดจอ", "distractors": ["โปรแกรมตัดต่อวิดีโอ", "โปรแกรมลบไวรัสในไดรฟ์", "ระบบจัดการฮาร์ดดิสก์"],
        "explanation": "DirectX และ Vulkan เป็น Graphics & Compute API ที่ช่วยให้ผู้พัฒนาเกมส่งคำสั่งเรนเดอร์กราฟิกไปยัง GPU โดยตรง"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ในโปรเซสเซอร์ 'Hyper-Threading' (SMT) ทำงานอย่างไรในระดับฮาร์ดแวร์?",
        "correct": "จำลอง 1 คอร์ฟิสิคัลให้มี 2 เธรดสถาปัตยกรรมทางลอจิคัล", "distractors": ["ติดตั้งชิป CPU เพิ่มเติมอีกหนึ่งตัว", "เพิ่มสัญญาณนาฬิกาเป็นสองเท่า", "ลดความร้อนของชิปลงครึ่งหนึ่ง"],
        "explanation": "Simultaneous Multithreading (SMT) แชร์หน่วยประมวลผลภายในคอร์เดียวกัน ทำให้รัน 2 เธรดพร้อมกันได้เมื่อมีหน่วยว่าง"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "ช่องเสียบพอร์ต 'USB-C' รองรับมาตรฐาน 'Thunderbolt 4' มีอัตราส่งข้อมูลสูงสุดเท่าใด?",
        "correct": "40 Gbps", "distractors": ["10 Gbps", "5 Gbps", "100 Gbps"],
        "explanation": "Thunderbolt 3 และ Thunderbolt 4 รองรับอัตราการส่งถ่ายข้อมูลแบนด์วิดท์สูงสุดที่ 40 Gbps"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "เทคนิค 'Trim' บนระบบปฏิบัติการมีประโยชน์ต่อไดรฟ์ SSD อย่างไร?",
        "correct": "แจ้งเตือนชิปแฟลชให้เคลียร์บล็อกข้อมูลที่ถูกลบ เพื่อคงความเร็วเขียน", "distractors": ["ตัดไฟอัตโนมัติเมื่อไดรฟ์ร้อน", "บีบอัดไฟล์ทุกไฟล์ให้เล็กลงครึ่งหนึ่ง", "แปลงไดรฟ์ SSD ให้เป็นแรมสำรอง"],
        "explanation": "คำสั่ง TRIM ช่วยให้ระบบปฏิบัติการแจ้ง SSD ว่าบล็อกข้อมูลใดไม่ใช้งานแล้ว เพื่อทำ Garbage Collection ล่วงหน้า"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "เหตุใดการกดปุ่ม 'Power ค้างไว้ 5 วินาที' เพื่อบังคับปิดเครื่องจึงอาจทำให้เกิดปัญหา?",
        "correct": "ข้อมูลที่ค้างอยู่ในแคชและไฟล์ระบบอาจเขียนไม่เสร็จจนไฟล์พัง", "distractors": ["ทำให้ชิป CPU ละลายทันที", "ทำให้ไฟดับทั้งบ้าน", "ทำให้แป้นพิมพ์ล็อคถาวร"],
        "explanation": "การบังคับตัดไฟกะทันหันทำให้ OS ไม่มีเวลา Flush ข้อมูลจาก RAM ลงดิสก์ ส่งผลให้ File System เสียหายได้"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "สายไฟแบบ 'SATA Data Cable' สำหรับฮาร์ดดิสก์แบบมาตรฐานมีขั้วสัมผัสกี่พิน (Pins)?",
        "correct": "7 พิน", "distractors": ["15 พิน", "4 พิน", "24 พิน"],
        "explanation": "SATA Data มี 7 พิน (ส่วนสายไฟ SATA Power มี 15 พิน และสาย IDE แบบเก่ามี 40/80 พิน)"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ในการระบายความร้อนคอมพิวเตอร์ 'Vapor Chamber' ทำงานโดยใช้หลักการใด?",
        "correct": "การระเหยและควบแน่นของของเหลวในแผ่นโลหะสุญญากาศ", "distractors": ["การเป่าลมเย็นผ่านพัดลมไอพ่น", "การใช้สารเคมีดูดความเย็น", "การใช้น้ำแข็งแห้งหล่อเลี้ยง"],
        "explanation": "Vapor Chamber ใช้ของเหลวเปลี่ยนสถานะเป็นไอเพื่อกระจายความร้อนอย่างรวดเร็วทั่วแผ่นทองแดงก่อนควบแน่นกลับ"
    },
    {
        "category_key": "cat_basic", "difficulty": "ปานกลาง",
        "text": "เซนเซอร์ 'Lidar' ที่เริ่มนำมาใช้ในสมาร์ตโฟนและรถยนต์ไร้คนขับ วัดระยะวัตถุด้วยสิ่งใด?",
        "correct": "ลำแสงเลเซอร์ (Light Detection and Ranging)", "distractors": ["คลื่นเสียงความถี่สูง", "คลื่นวิทยุแม่เหล็กไฟฟ้า", "การสัมผัสทางกายภาพ"],
        "explanation": "LiDAR ยิงพัลส์แสงเลเซอร์ออกไปและจับเวลาที่สะท้อนกลับมาเพื่อสร้างแผนที่ 3 มิติความแม่นยำสูง"
    },
    {
        "category_key": "cat_basic", "difficulty": "ยาก",
        "text": "ในจอภาพ ค่าขอบเขตสี 'DCI-P3' แตกต่างจาก 'sRGB' อย่างไร?",
        "correct": "DCI-P3 ให้ขอบเขตสีที่กว้างกว่า โดยเฉพาะเฉดสีแดงและเขียว", "distractors": ["DCI-P3 แสดงได้เฉพาะภาพขาวดำ", "sRGB ให้สีสันสดใสกว่าจอโรงภาพยนตร์", "ทั้งสองมาตรฐานให้ขอบเขตสีเท่ากันทุกประการ"],
        "explanation": "DCI-P3 เป็นมาตรฐานสีในวงการภาพยนตร์ดิจิทัล ครอบคลุมสีกว้างกว่ามาตรฐาน sRGB ประมาณ 25%"
    },

    # -------------------------------------------------------------
    # Category 2: Operating Systems, Linux, Low-Level, Process & Memory (35 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบปฏิบัติการ 'Zombie Process' คือโปรเซสที่มีลักษณะอย่างไร?",
        "correct": "ทำงานเสร็จสิ้นแล้วแต่ Process Table ยังไม่ถูกลบเพราะ Parent ยังไม่อ่าน Exit Status", "distractors": ["โปรเซสที่ติดไวรัสและแอบขโมยข้อมูล", "โปรเซสที่วนลูปไม่สิ้นสุดจน CPU เต็ม 100%", "โปรเซสที่ถูกระงับการทำงานชั่วคราว"],
        "explanation": "Zombie Process คือโปรเซสที่จบการทำงานแล้วแต่ยังคงมีข้อมูลตกค้างในตารางโปรเซสเพื่อรอให้ Parent เรียก wait()"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบปฏิบัติการ 'Orphan Process' หมายถึงโปรเซสในลักษณะใด?",
        "correct": "โปรเซสลูกที่ Parent สิ้นสุดการทำงานไปก่อน และถูกรับเลี้ยงโดย Init/systemd", "distractors": ["โปรเซสที่ไม่มีสิทธิ์เข้าถึงอินเทอร์เน็ต", "โปรเซสที่ไม่ยอมใช้หน่วยความจำแรม", "โปรเซสที่ถูกลบออกจากฮาร์ดดิสก์"],
        "explanation": "เมื่อ Parent จบก่อน Child โปรเซสลูกนั้นจะกลายเป็น Orphan Process และระบบจะโอน Parent ID ให้ Init (PID 1) รับดูแล"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "สถานะของโปรเซสข้อใดที่พร้อมทำงานและรอเพียงให้ CPU ถูกจัดสรรมาให้ (CPU Scheduling)?",
        "correct": "Ready State", "distractors": ["Blocked/Waiting State", "New State", "Terminated State"],
        "explanation": "สถานะ Ready คือเตรียมพร้อมทุกอย่างครบแล้ว ข้อมูลอยู่ใน RAM รอเพียง OS Dispatcher มอบเวลา CPU ให้รัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบจัดการหน่วยความจำ 'Thrashing' เกิดขึ้นจากสาเหตุใด?",
        "correct": "ระบบใช้เวลาส่วนใหญ่สลับ Page เข้าออกระหว่าง RAM กับ Disk จนแทบไม่ได้ทำงานจริง", "distractors": ["ฮาร์ดดิสก์เกิดความร้อนสูงจนหยุดหมุน", "โปรแกรมถูกลบออกจากเครื่องโดยไม่ตั้งใจ", "ผู้ใช้เปิดหน้าจอพร้อมกันหลายจอ"],
        "explanation": "Thrashing เกิดเมื่อ RAM ไม่พออย่างรุนแรง ระบบจึงมัวแต่ทำ Paging สลับข้อมูลไปมาจนเครื่องค้างสนิท"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ฮาร์ดแวร์แคช 'TLB' (Translation Lookaside Buffer) มีหน้าที่สำคัญอะไรในระบบ Virtual Memory?",
        "correct": "แคชการแปลง Virtual Address เป็น Physical Address เพื่อลดเวลาเข้าถึงตาราง Page", "distractors": ["ทำความสะอาดข้อมูลขยะในแรม", "ควบคุมพัดลมซีพียู", "บันทึกรหัสผ่านของผู้ดูแลระบบ"],
        "explanation": "TLB เป็นแคชความเร็วสูงใน MMU (Memory Management Unit) ช่วยจำคู่แปลแอดเดรสเสมือนให้เป็นแอดเดรสจริงในแรม"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบไฟล์ Linux โครงสร้าง 'Inode' (Index Node) เก็บข้อมูลอะไรบ้าง?",
        "correct": "ขนาดไฟล์, สิทธิ์การเข้าถึง, เจ้าของ และตำแหน่งบล็อกบนดิสก์ (ยกเว้นชื่อไฟล์)", "distractors": ["ชื่อไฟล์และข้อความทั้งหมดในไฟล์", "เฉพาะรหัสผ่านของไฟล์เท่านั้น", "ภาพตัวอย่าง Thumbnail ของไฟล์"],
        "explanation": "Inode เก็บ Metadata และ Data Pointer ของไฟล์ทั้งหมด แต่ชื่อไฟล์จะถูกเก็บไว้ในโครงสร้าง Directory Entry"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่ง Linux 'chmod 755 filename' กำหนดสิทธิ์ให้กลุ่ม 'Other' (ผู้อื่น) ทำอะไรได้บ้าง?",
        "correct": "อ่านและรันได้เท่านั้น (r-x = 5)", "distractors": ["อ่าน เขียน และรันได้ครบ (rwx = 7)", "อ่านได้อย่างเดียว (r-- = 4)", "ห้ามเข้าถึงโดยเด็ดขาด (--- = 0)"],
        "explanation": "เลขฐานแปด: 7 (Owner: rwx), 5 (Group: r-x), 5 (Other: r-x) โดย 5 มาจาก Read (4) + Execute (1)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในระบบ Linux การสร้าง 'Hard Link' แตกต่างจาก 'Symbolic Link' (Soft Link) อย่างไร?",
        "correct": "Hard Link ชี้ไปยัง Inode เดียวกันโดยตรง แม้ลบไฟล์ต้นฉบับข้อมูลก็ยังคงอยู่", "distractors": ["Hard Link สามารถเชื่อมโยงข้ามฮาร์ดดิสก์คนละลูกได้", "Soft Link ไม่สามารถเปิดอ่านข้อความได้", "Hard Link ใช้เนื้อที่ดิสก์เพิ่มขึ้น 2 เท่า"],
        "explanation": "Hard Link เพิ่ม Reference Count ไปยัง Inode เดียวกัน ส่วน Soft Link เป็นไฟล์พิเศษที่เก็บ Path ชี้ไปยังชื่อไฟล์เป้าหมาย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กลไก IPC (Inter-Process Communication) ข้อใดมีความเร็วในการแลกเปลี่ยนข้อมูลระหว่างโปรเซสสูงที่สุด?",
        "correct": "Shared Memory (หน่วยความจำร่วม)", "distractors": ["Pipes (ไปป์)", "Unix Domain Sockets", "Message Queues"],
        "explanation": "Shared Memory อนุญาตให้โปรเซสเข้าถึง RAM บล็อกเดียวกันโดยตรง จึงเร็วที่สุดโดยไม่ต้องผ่าน System Call คัดลอกข้อมูลซ้ำ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "สถาปัตยกรรมเคอร์เนลแบบ 'Microkernel' แตกต่างจาก 'Monolithic Kernel' อย่างไร?",
        "correct": "ย้ายไดรเวอร์และระบบไฟล์ไปทำงานใน User Space ให้เคอร์เนลเหลือเฉพาะฟังก์ชันพื้นฐาน", "distractors": ["มีขนาดไฟล์ใหญ่กว่าและกินแรมมากกว่า", "ไม่รองรับการทำงานแบบมัลติทาสกิ้ง", "ไม่สามารถเชื่อมต่อเครือข่ายอินเทอร์เน็ตได้"],
        "explanation": "Microkernel เน้นความเสถียรและความปลอดภัย โดยรันไดรเวอร์และบริการต่าง ๆ ใน User Space เพื่อป้องกันระบบล่มทั้งระบบ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่ง Linux ใดใช้สำหรับค้นหาข้อความตามรูปแบบ Regular Expression ภายในไฟล์อย่างรวดเร็ว?",
        "correct": "grep", "distractors": ["cat", "ls", "pwd"],
        "explanation": "grep (Global Regular Expression Print) เป็นเครื่องมือมาตรฐานยอดนิยมในการค้นหาแพตเทิร์นข้อความในไฟล์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่ง Linux ใดใช้แสดงและติดตามโปรเซสที่กำลังทำงานอยู่แบบเรียลไทม์ พร้อมการใช้งาน CPU/RAM?",
        "correct": "top / htop", "distractors": ["mkdir", "touch", "chmod"],
        "explanation": "top หรือ htop แสดงตารางโปรเซส การใช้ CPU, หน่วยความจำ และ Load Average ของระบบแบบเรียลไทม์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบปฏิบัติการ 'System Call' (Syscall) คืออะไร?",
        "correct": "ช่องทางที่โปรแกรมใน User Mode ร้องขอรับบริการจาก Kernel Mode", "distractors": ["การโทรศัพท์หาเจ้าหน้าที่ดูแลระบบ", "คำสั่งเปิดโปรแกรมคิดเลข", "การสแกนหาข้อผิดพลาดของคีย์บอร์ด"],
        "explanation": "Syscall คืออินเทอร์เฟซมาตรฐานระหว่าง Application กับ OS Kernel เช่น การเปิดไฟล์ (open), การสร้างโปรเซส (fork)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "สัญญาณ Signal ในระบบ Linux ข้อใดมีผลบังคับปิดโปรเซสทันทีโดยที่โปรเซสไม่สามารถดักจับหรือเพิกเฉยได้?",
        "correct": "SIGKILL (Signal 9)", "distractors": ["SIGTERM (Signal 15)", "SIGINT (Signal 2)", "SIGHUP (Signal 1)"],
        "explanation": "SIGKILL (kill -9) สั่งให้เคอร์เนลยุติโปรเซสเป้าหมายทันที โดยไม่เปิดโอกาสให้โปรเซส Cleanup ทรัพยากร"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ฟังก์ชัน 'fork()' ในระบบปฏิบัติการตระกูล POSIX/Linux ทำหน้าที่อะไร?",
        "correct": "สร้างโปรเซสลูกขึ้นมาใหม่ โดยคัดลอกสถานะและหน่วยความจำจากโปรเซสแม่", "distractors": ["ปิดคอมพิวเตอร์ทันที", "แยกสายไฟออกเป็นสองเส้น", "แปลงภาษา C เป็นไพทอน"],
        "explanation": "fork() สร้าง Child Process ที่เหมือนกับ Parent Process ทุกประการ และส่งคืนค่า PID ให้โปรเซสแม่และ 0 ให้โปรเซสลูก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิค 'Copy-on-Write' (CoW) เมื่อมีการเรียกใช้ fork() มีประโยชน์อย่างไร?",
        "correct": "หน่วงเวลาการคัดลอก RAM จริงไว้จนกว่าจะมีโปรเซสใดพยายามแก้ไขข้อมูล", "distractors": ["พิมพ์เอกสารซ้ำสองฉบับทันที", "สำรองข้อมูลลงคลาวด์ทุกวินาที", "ป้องกันการกดปุ่มคัดลอกบนแป้นพิมพ์"],
        "explanation": "CoW ช่วยประหยัดหน่วยความจำอย่างมาก โดยให้ Parent และ Child แชร์ Page เดียวกันจนกว่าจะมีการ Write ข้อมูลลง Page นั้น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ใน Windows ไดเรกทอรี 'System32' มีความสำคัญอย่างไร?",
        "correct": "เป็นที่เก็บไฟล์ระบบปฏิบัติการ ไดรเวอร์ และไฟล์ .dll หลักของ Windows", "distractors": ["เป็นโฟลเดอร์สำหรับเก็บไฟล์เพลงชั่วคราว", "เป็นถังขยะสำรองของระบบ", "เป็นโฟลเดอร์สำหรับเกม 32 บิตเท่านั้น"],
        "explanation": "System32 คือหัวใจหลักของ Windows ซึ่งบรรจุ Executable และ Dynamic Link Libraries (DLLs) สำคัญของระบบ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ระบบ 'Virtual Memory' กำหนดให้โปรแกรมแต่ละตัวมองเห็นพื้นที่หน่วยความจำของตนเองอย่างไร?",
        "correct": "มองเห็นเป็นพื้นที่แอดเดรสต่อเนื่องแบบเสมือน (Virtual Address Space)", "distractors": ["มองเห็นตำแหน่งชิปแรมจริงบนเมนบอร์ด", "มองเห็นข้อมูลของโปรแกรมอื่นทั้งหมดอย่างอิสระ", "แชร์แอดเดรสตัวเลขเดียวกันกับทุกโปรแกรม"],
        "explanation": "Virtual Memory สร้างภาพลวงตาให้แต่ละโปรเซสคิดว่าตนเองเป็นเจ้าของพื้นที่หน่วยความจำขนาดใหญ่และแยกเป็นอิสระจากโปรเซสอื่น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรเซสแรกสุดที่ถูกสร้างขึ้นเมื่อบูตระบบปฏิบัติการ Linux สำเร็จ (PID 1) ปัจจุบันมักคือโปรแกรมใด?",
        "correct": "systemd (หรือ init)", "distractors": ["bash", "kernel", "grub"],
        "explanation": "systemd เป็น Init System ตัวแรกของ Linux (PID = 1) ทำหน้าที่เริ่มต้นบริการและจัดการโปรเซสอื่น ๆ ทั้งหมดในระบบ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ตัวแปรสภาพแวดล้อม 'PATH' ในระบบปฏิบัติการมีหน้าที่อะไร?",
        "correct": "ระบุรายชื่อโฟลเดอร์ที่ระบบจะเข้าไปค้นหาไฟล์โปรแกรมเมื่อพิมพ์คำสั่ง", "distractors": ["เก็บรหัสผ่านของผู้ใช้งานทั้งหมด", "ระบุเส้นทางของสัญญาณดาวเทียม", "จำกัดความเร็วการเชื่อมต่ออินเทอร์เน็ต"],
        "explanation": "เมื่อผู้ใช้พิมพ์คำสั่งใน Terminal ระบบจะไล่ค้นหาโปรแกรมตามโฟลเดอร์ต่าง ๆ ที่ระบุไว้ในตัวแปร PATH"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เงื่อนไขข้อใด 'ไม่ใช่' 1 ใน 4 เงื่อนไขของ Coffman ที่ทำให้เกิดสภาวะ Deadlock?",
        "correct": "Preemption (การแย่งชิงทรัพยากรคืนได้)", "distractors": ["Mutual Exclusion", "Hold and Wait", "Circular Wait"],
        "explanation": "4 เงื่อนไขของ Deadlock คือ: Mutual Exclusion, Hold & Wait, No Preemption (ห้ามแย่งทรัพยากรคืน), Circular Wait"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมจัดตารางซีพียูแบบ 'Round Robin' (RR) ใช้สิ่งใดในการสลับการทำงานของแต่ละโปรเซส?",
        "correct": "Time Quantum (ช่วงเวลาคงที่)", "distractors": ["ขนาดไฟล์ของโปรแกรม", "อายุของผู้ใช้เครื่อง", "ความยาวของชื่อโปรเซส"],
        "explanation": "Round Robin กำหนด Time Slice/Quantum ให้แต่ละโปรเซสรันเท่า ๆ กันตามคิวแบบหมุนเวียน (Preemptive)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ไฟล์ '/etc/hosts' ในระบบปฏิบัติการทำหน้าที่อะไร?",
        "correct": "จับคู่ชื่อโดเมนกับ IP Address ภายในเครื่องก่อนถามเซิร์ฟเวอร์ DNS", "distractors": ["บันทึกประวัติการเข้าชมเว็บไซต์ทั้งหมด", "เก็บรายชื่อเพื่อนในอีเมล", "บล็อกไม่ให้เปิดเครื่องคอมพิวเตอร์"],
        "explanation": "hosts file เป็นตารางแปลง Domain เป็น IP ในระดับ Local เครื่องจะตรวจสอบไฟล์นี้ก่อนส่งคำขอไปยัง DNS เสมอ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ปัญหาความปลอดภัยแบบ 'Buffer Overflow' เกิดขึ้นได้อย่างไรในระดับหน่วยความจำ?",
        "correct": "โปรแกรมเขียนข้อมูลเกินขอบเขตของ Buffer จนล้นไปทับพื้นที่หน่วยความจำข้างเคียง", "distractors": ["ฮาร์ดดิสก์อ่านข้อมูลไม่ทันจนเครื่องค้าง", "การเปิดแท็บเบราว์เซอร์มากเกินไป", "สายแลนส่งสัญญาณเร็วเกินไป"],
        "explanation": "Buffer Overflow เกิดเมื่อไม่มีการตรวจสอบขนาด Boundary ข้อมูลส่วนเกินจะล้นไปทับ Return Address ทำให้แฮกเกอร์รันโค้ดอันตรายได้"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ระบบไฟล์แบบ 'ZFS' หรือ 'Btrfs' มีความสามารถพิเศษ 'Copy-on-Write' สำหรับทำสิ่งใดได้อย่างรวดเร็วในเสี้ยววินาที?",
        "correct": "การสร้างจุดย้อนกลับและภาพถ่ายสถานะข้อมูล (Snapshots)", "distractors": ["การสแกนหาฝุ่นในฮาร์ดดิสก์", "การแปลงเพลงเป็นวิดีโอ 4K", "การเพิ่มความเร็วการหมุนของพัดลม"],
        "explanation": "CoW File System ทำให้สร้าง Snapshot ได้ทันทีโดยไม่ต้องคัดลอกข้อมูลซ้ำจนกว่าจะมีการแก้ไขบล็อกนั้น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่ง 'sudo' ในระบบ Linux ย่อมาจากคำว่าอะไร?",
        "correct": "Superuser Do", "distractors": ["System Universal Data Output", "Standard User Delete Option", "Security User Device Operation"],
        "explanation": "sudo อนุญาตให้ผู้ใช้ที่ได้รับอนุญาตรันคำสั่งด้วยสิทธิ์ของผู้ดูแลระบบสูงสุด (Superuser / Root)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กลไก 'Counting Semaphore' แตกต่างจาก 'Binary Semaphore' อย่างไร?",
        "correct": "Counting Semaphore อนุญาตให้มีทรัพยากรพร้อมใช้งานได้มากกว่า 1 ชิ้นพร้อมกัน", "distractors": ["Counting Semaphore ใช้งานได้เฉพาะกับเลขฐานสอง", "Binary Semaphore รองรับได้ไม่จำกัดจำนวนเธรด", "ทั้งสองตัวทำงานเหมือนกันทุกประการ"],
        "explanation": "Binary Semaphore มีค่า 0 หรือ 1 (คล้าย Mutex) ส่วน Counting Semaphore มีค่าจำนวนเต็มบวกตามจำนวนทรัพยากรที่มีอยู่"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบสถาปัตยกรรม x86 'Ring 0' หมายถึงระดับสิทธิ์ (Privilege Level) ใด?",
        "correct": "ระดับสูงสุดของ Kernel Space ที่เข้าถึงฮาร์ดแวร์ได้โดยตรง", "distractors": ["ระดับ User Space สำหรับโปรแกรมทั่วไป", "ระดับไดรเวอร์จอภาพเท่านั้น", "ระดับที่ไม่สามารถสั่งการคอมพิวเตอร์ได้"],
        "explanation": "สถาปัตยกรรม CPU x86 แบ่งเป็น 4 Rings โดย Ring 0 คือระดับ Kernel Space (สิทธิ์สูงสุด) และ Ring 3 คือ User Applications"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ระบบปฏิบัติการ 'Linux' มีพื้นฐานพัฒนาตามมาตรฐานและแนวคิดของระบบปฏิบัติการใดในอดีต?",
        "correct": "Unix", "distractors": ["Windows 95", "DOS", "Symbian"],
        "explanation": "Linus Torvalds พัฒนาเคอร์เนล Linux โดยได้รับแรงบันดาลใจจาก Unix และออกแบบให้สอดคล้องตามมาตรฐาน POSIX"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "คำสั่ง 'kill -l' ใน Linux Terminal ใช้สำหรับทำอะไร?",
        "correct": "แสดงรายชื่อสัญญาณระบบ (Signals) ทั้งหมดที่รองรับ", "distractors": ["ลบไฟล์ทั้งหมดในเครื่องทิ้งทันที", "แสดงรายชื่อผู้ใช้ที่ถูกแบน", "ปิดหน้าจอคอมพิวเตอร์"],
        "explanation": "kill -l จะพิมพ์รายชื่อ Signals ทั้งหมด เช่น SIGHUP, SIGINT, SIGKILL, SIGSEGV, SIGTERM"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ข้อผิดพลาด 'Segmentation Fault' (Segfault) มักเกิดจากการกระทำข้อใดของโปรแกรม?",
        "correct": "โปรแกรมพยายามเข้าถึงหรือเขียนพื้นที่หน่วยความจำที่ตนเองไม่มีสิทธิ์ (เช่น Null Pointer)", "distractors": ["ฮาร์ดดิสก์เกิด Bad Sector ทางกายภาพ", "คีย์บอร์ดพิมพ์ตัวอักษรไม่ติด", "สายสัญญาณภาพหลวม"],
        "explanation": "Segfault เกิดเมื่อโปรแกรมเข้าถึง Memory ที่ไม่ได้รับอนุญาต (เช่น Dereference Null Pointer หรือชี้ออกนอก Array) OS จึงสั่งยุติทันที"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่ง 'tar -czvf backup.tar.gz /data' ตัวอักษร 'z' มีหน้าที่อะไร?",
        "correct": "บีบอัดข้อมูลด้วยอัลกอริทึม gzip", "distractors": ["ซูมขยายหน้าจอขึ้น 2 เท่า", "ลบโฟลเดอร์ต้นทางทิ้ง", "ตั้งรหัสผ่านความปลอดภัย"],
        "explanation": "ในคำสั่ง tar: c=create, z=gzip compression, v=verbose, f=file name"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบ Linux ไดเรกทอรีเสมือน '/proc' ทำหน้าที่เป็นตัวกลางสำหรับอะไร?",
        "correct": "เป็น Pseudo-filesystem ที่แสดงข้อมูลสถานะเคอร์เนลและโปรเซสแบบเรียลไทม์", "distractors": ["เป็นที่เก็บไฟล์เอกสารของผู้ใช้งาน", "เป็นโฟลเดอร์ติดตั้งเกมทั้งหมด", "เป็นไดรฟ์สำรองของระบบคลาวด์"],
        "explanation": "/proc เป็น Virtual Filesystem ที่ไม่ได้อยู่บนดิสก์จริง แต่สร้างขึ้นใน RAM เพื่อให้ดูข้อมูล Hardware และ Process (เช่น /proc/cpuinfo, /proc/meminfo)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "โปรแกรมประเภท 'Package Manager' บน Ubuntu/Debian Linux คือคำสั่งใด?",
        "correct": "apt / apt-get", "distractors": ["yum", "pacman", "brew"],
        "explanation": "Debian และ Ubuntu ใช้ APT (Advanced Package Tool) ในการติดตั้ง อัปเดต และจัดการซอฟต์แวร์แพ็กเกจ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ไฟล์ '/etc/passwd' ใน Linux ใช้เก็บข้อมูลอะไรเป็นหลัก?",
        "correct": "รายชื่อบัญชีผู้ใช้, User ID (UID), Group ID (GID) และ Home Directory", "distractors": ["รหัสผ่านที่ไม่ได้เข้ารหัสของผู้ใช้ทุกคน", "รหัสผ่าน Wi-Fi ทั้งหมดในบ้าน", "ประวัติการค้นหาบนกูเกิล"],
        "explanation": "/etc/passwd เก็บข้อมูลบัญชีผู้ใช้และสิทธิ์พื้นฐาน (ส่วน Password Hash ที่เข้ารหัสจะถูกเก็บแยกไว้อย่างปลอดภัยใน /etc/shadow)"
    },

    # -------------------------------------------------------------
    # Category 3: Networking, Protocols & Web Infrastructure (35 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เครือข่ายที่มี Subnet Mask เป็น '/28' (255.255.255.240) สามารถมีเครื่องโฮสต์ (Usable Hosts) ใช้งานได้สูงสุดกี่เครื่อง?",
        "correct": "14 เครื่อง", "distractors": ["16 เครื่อง", "30 เครื่อง", "6 เครื่อง"],
        "explanation": "สูตร $2^{(32-28)} - 2 = 16 - 2 = 14$ เครื่อง (หัก Network Address และ Broadcast Address ออก 2 แอดเดรส)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หมายเลข IP Address ในข้อใดจัดเป็น 'Private IP Address' ตามมาตรฐาน RFC 1918?",
        "correct": "172.20.15.1", "distractors": ["172.35.10.2", "8.8.8.8", "1.1.1.1"],
        "explanation": "ช่วง Private IP: Class A (10.0.0.0/8), Class B (172.16.0.0 - 172.31.255.255), Class C (192.168.0.0/16)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "หากอุปกรณ์ได้รับหมายเลข IP ขึ้นต้นด้วย '169.254.x.x' (APIPA) แสดงว่าเกิดปัญหาใด?",
        "correct": "อุปกรณ์ไม่สามารถติดต่อกับเซิร์ฟเวอร์ DHCP เพื่อขอรับ IP ได้", "distractors": ["อินเทอร์เน็ตมีความเร็วสูงระดับ 10 Gbps", "อุปกรณ์ถูกแฮกเกอร์ขโมยรหัสผ่าน", "หน้าจอคอมพิวเตอร์เสีย"],
        "explanation": "APIPA (Automatic Private IP Addressing) 169.254.0.0/16 จะถูกกำหนดอัตโนมัติเมื่อเครื่องหา DHCP Server ไม่พบ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโมเดล OSI 7 เลเยอร์ หน่วยข้อมูล (PDU) ในเลเยอร์ที่ 2 (Data Link Layer) เรียกว่าอะไร?",
        "correct": "เฟรม (Frame)", "distractors": ["แพ็กเก็ต (Packet)", "เซกเมนต์ (Segment)", "บิต (Bit)"],
        "explanation": "Layer 1 = Bit, Layer 2 = Frame, Layer 3 = Packet, Layer 4 = Segment, Layer 5-7 = Data"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เรคอร์ดของระบบ DNS ประเภท 'AAAA Record' มีหน้าที่อะไร?",
        "correct": "จับคู่ชื่อโดเมนกับหมายเลข IPv6 Address (128 บิต)", "distractors": ["จับคู่ชื่อโดเมนกับหมายเลข IPv4 Address (32 บิต)", "ระบุเซิร์ฟเวอร์รับส่งอีเมล (Mail Server)", "สร้างชื่อโดเมนเสมือน (Alias)"],
        "explanation": "A Record แปลงเป็น IPv4 ส่วน AAAA Record (Quad-A) แปลงเป็น IPv6"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ค่า 'TTL' (Time to Live) ในส่วนหัวของ IP Packet มีประโยชน์หลักเพื่ออะไร?",
        "correct": "ป้องกันไม่ให้แพ็กเก็ตวิ่งวนในเครือข่ายอย่างไม่รู้จบ (Routing Loop)", "distractors": ["กำหนดเวลาหมดอายุของรหัสผ่านผู้ใช้", "วัดระยะเวลาที่ใช้ในการดาวน์โหลดไฟล์", "บันทึกเวลาเปิดเครื่องคอมพิวเตอร์"],
        "explanation": "TTL จะลดลง 1 ทุกครั้งที่ผ่าน Router 1 Hop หากลดเหลือ 0 แพ็กเก็ตจะถูกทิ้งและแจ้งกลับด้วย ICMP Time Exceeded"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอลการจัดเส้นทางหลักที่เชื่อมโยงระบบเครือข่ายของ ISP ทั่วโลกเข้าด้วยกันบนอินเทอร์เน็ตคือโปรโตคอลใด?",
        "correct": "BGP (Border Gateway Protocol)", "distractors": ["OSPF", "RIP", "EIGRP"],
        "explanation": "BGP คือโปรโตคอลแบบ Path Vector ที่ใช้แลกเปลี่ยนเส้นทางระหว่าง Autonomous Systems (AS) บนอินเทอร์เน็ตทั่วโลก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอล 'HTTP/2' มีจุดเด่นเหนือ 'HTTP/1.1' ในเรื่องใดชัดเจนที่สุด?",
        "correct": "Multiplexing ส่งข้อมูลได้หลาย Request พร้อมกันใน 1 การเชื่อมต่อ TCP", "distractors": ["ไม่ต้องใช้การเชื่อมต่ออินเทอร์เน็ต", "เปลี่ยนไปใช้สายโทรศัพท์แทนสายแลน", "ยกเลิกการใช้โค้ด HTML"],
        "explanation": "HTTP/2 นำเสนอ Binary Framing และ Multiplexing ช่วยแก้ปัญหา Head-of-Line Blocking ในระดับ Application Layer"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอล 'HTTP/3' เปลี่ยนแปลงโครงสร้างการทำงานโดยทำงานบนพื้นฐานของโปรโตคอลใด?",
        "correct": "QUIC (ซึ่งทำงานบน UDP)", "distractors": ["TCP แบบดั้งเดิม", "ICMP", "FTP"],
        "explanation": "HTTP/3 ทำงานบนโปรโตคอล QUIC (บน UDP) ช่วยลด Latency ในการ Handshake และแก้ปัญหา Head-of-Line Blocking ระดับ Transport"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "รหัสสถานะ HTTP Code '301 Moved Permanently' บ่งบอกถึงสิ่งใด?",
        "correct": "หน้าเว็บหรือทรัพยากรถูกย้ายไปยัง URL ใหม่เป็นการถาวร", "distractors": ["ผู้ใช้งานใส่รหัสผ่านผิด", "เซิร์ฟเวอร์ปิดให้บริการถาวร", "หน้าเว็บกำลังถูกโจมตีด้วยไวรัส"],
        "explanation": "HTTP 301 สั่งให้เบราว์เซอร์ Redirect ไปยัง URL ใหม่ และ Search Engine จะถ่ายโอนคะแนน SEO ไปยังที่อยู่ใหม่อัตโนมัติ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "รหัสสถานะ HTTP Code '429 Too Many Requests' เกิดขึ้นจากสาเหตุใด?",
        "correct": "ผู้ใช้หรือโปรแกรมส่งคำขอถี่เกินกว่าอัตรา Rate Limit ที่เซิร์ฟเวอร์กำหนด", "distractors": ["เซิร์ฟเวอร์ไม่มีการเชื่อมต่อกับอินเทอร์เน็ต", "รหัสผ่านหมดอายุการใช้งาน", "ขนาดรูปภาพใหญ่เกินไป"],
        "explanation": "HTTP 429 แจ้งว่า Client ส่ง Request บ่อยเกินขีดจำกัด (Rate Limiting) เพื่อป้องกันเซิร์ฟเวอร์โอเวอร์โหลด"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "รหัสสถานะ HTTP Code '502 Bad Gateway' หมายถึงข้อใด?",
        "correct": "เซิร์ฟเวอร์ที่เป็น Proxy/Gateway ได้รับคำตอบที่ผิดพลาดจากเซิร์ฟเวอร์ต้นทาง (Upstream)", "distractors": ["รหัสผ่านของผู้ดูแลระบบไม่ถูกต้อง", "คอมพิวเตอร์ของผู้ใช้ติดไวรัส", "สายแลนของผู้ใช้หลุด"],
        "explanation": "HTTP 502 เกิดขึ้นเมื่อ Reverse Proxy (เช่น Nginx) พยายามคุยกับ Backend Application Server แต่ได้รับการตอบกลับที่ล้มเหลว"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคโนโลยี 'WebSocket' มีข้อได้เปรียบเหนือการร้องขอแบบ HTTP ทั่วไปอย่างไร?",
        "correct": "สร้างช่องทางการสื่อสารแบบ Full-Duplex สองทิศทางแบบเรียลไทม์ในการเชื่อมต่อเดียว", "distractors": ["ทำให้สามารถดาวน์โหลดเกมได้โดยไม่ต้องใช้อินเทอร์เน็ต", "แปลงหน้าเว็บเป็นวิดีโอ 8K อัตโนมัติ", "เพิ่มความจุของฮาร์ดดิสก์เซิร์ฟเวอร์"],
        "explanation": "WebSocket ให้การสื่อสารแบบสองทิศทางตลอดเวลา (Persistent Connection) เหมาะสำหรับ Live Chat, การเงิน หรือเกมออนไลน์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "บริการเครือข่ายส่งมอบเนื้อหา 'CDN' (Content Delivery Network) ทำงานอย่างไรเพื่อเร่งความเร็วเว็บ?",
        "correct": "แคชสำเนาข้อมูลไว้ที่ Edge Server ใกล้ตำแหน่งผู้ใช้งานทั่วโลก", "distractors": ["บีบอัดไฟล์เว็บให้เหลือขนาด 0 ไบต์", "เพิ่มความเร็วสัญญาณ Wi-Fi ที่บ้านผู้ใช้", "ปิดการใช้งานรูปภาพบนเว็บไซต์"],
        "explanation": "CDN วางเซิร์ฟเวอร์กระจายตัวทั่วโลกและเสิร์ฟ Static Files จากจุดที่ใกล้ผู้ใช้งานที่สุดเพื่อลดความหน่วง (Latency)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโปรโตคอล TCP แฟล็ก 'RST' (Reset) ถูกส่งออกไปในสถานการณ์ใด?",
        "correct": "ปฏิเสธหรือสั่งยกเลิกการเชื่อมต่อกะทันหันเนื่องจากพอร์ตปิดหรือไม่ถูกต้อง", "distractors": ["ขอเริ่มต้นสร้างการเชื่อมต่อใหม่ตามขั้นตอนปกติ", "ยืนยันการรับแพ็กเก็ตข้อมูลสำเร็จ", "ขอส่งข้อความด่วนพิเศษ"],
        "explanation": "TCP RST ใช้ตัดการเชื่อมต่อทันทีเมื่อพบความผิดปกติ เช่น พยายามเชื่อมต่อไปยัง Port ที่ไม่มี Service รันอยู่"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอล 'ICMP' (Internet Control Message Protocol) เป็นพื้นฐานคำสั่งตรวจสอบเครือข่ายข้อใด?",
        "correct": "ping และ traceroute", "distractors": ["curl และ wget", "ssh และ telnet", "http และ https"],
        "explanation": "คำสั่ง ping ใช้แพ็กเก็ต ICMP Echo Request และ Echo Reply ในการทดสอบการเข้าถึงและความเร็วหน่วงของโฮสต์ปลายทาง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เซิร์ฟเวอร์แบบ 'Reverse Proxy' (เช่น Nginx) ทำหน้าที่แตกต่างจาก 'Forward Proxy' อย่างไร?",
        "correct": "Reverse Proxy ทำหน้าที่แทนและปกป้องกลุ่ม Web Server ฝั่งเซิร์ฟเวอร์", "distractors": ["Forward Proxy ใช้เฉพาะสำหรับเล่นเกมออนไลน์", "Reverse Proxy ติดตั้งอยู่บนเครื่องผู้ใช้งานตามบ้าน", "ทั้งสองทำหน้าที่เหมือนกันทุกประการ"],
        "explanation": "Forward Proxy ปกป้องและเป็นตัวแทน Client ภายใน ส่วน Reverse Proxy ปกป้องและทำ Load Balancing ให้กับ Server ภายนอก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "พอร์ตมาตรฐานของโปรโตคอล 'SSH' สำหรับการรีโมตควบคุมเซิร์ฟเวอร์อย่างปลอดภัยคือพอร์ตใด?",
        "correct": "พอร์ต 22", "distractors": ["พอร์ต 21 (FTP)", "พอร์ต 23 (Telnet)", "พอร์ต 25 (SMTP)"],
        "explanation": "SSH (Secure Shell) ใช้พอร์ต TCP 22 เป็นค่าเริ่มต้น ส่วน Telnet แบบไม่เข้ารหัสใช้พอร์ต 23"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "พอร์ตมาตรฐานของระบบ 'DNS' (Domain Name System) ในการสอบถามชื่อโดเมนคือพอร์ตใด?",
        "correct": "พอร์ต 53", "distractors": ["พอร์ต 80", "พอร์ต 443", "พอร์ต 110"],
        "explanation": "DNS Query ทั่วไปส่งผ่านพอร์ต UDP 53 (และใช้ TCP 53 สำหรับ Zone Transfer หรือข้อมูลขนาดใหญ่)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโปรโตคอล HTTP ข้อใดคือคุณสมบัติของเมธอดที่เป็น 'Idempotent'?",
        "correct": "การส่งคำขอคำสั่งเดิมซ้ำหลายครั้งจะให้ผลลัพธ์บนเซิร์ฟเวอร์เท่ากับการส่งเพียงครั้งเดียว", "distractors": ["คำขอที่ไม่มีการตอบกลับจากเซิร์ฟเวอร์", "คำขอที่ต้องเข้ารหัสด้วยกุญแจส่วนตัวเสมอ", "คำขอที่สามารถส่งได้เฉพาะผู้ดูแลระบบ"],
        "explanation": "Idempotent Methods (เช่น GET, PUT, DELETE, HEAD) ทำซ้ำกี่ครั้งสถานะของเซิร์ฟเวอร์ก็ยังคงเดิม ไม่เหมือน POST"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กระบวนการ 'DHCP DORA' มีลำดับขั้นตอนการขอรับ IP Address อย่างไร?",
        "correct": "Discover -> Offer -> Request -> Acknowledge", "distractors": ["Data -> Open -> Read -> Accept", "Direct -> Order -> Route -> Apply", "Download -> Overwrite -> Receive -> Allow"],
        "explanation": "ขั้นตอน DORA: Client ส่ง Discover (Broadcast) -> Server ตอบ Offer -> Client ส่ง Request -> Server ส่ง Ack ยืนยัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "หมายเลข 'IPv6' มีความยาวของแอดเดรสขนาดกี่บิต?",
        "correct": "128 บิต (แสดงผลด้วยเลขฐานสิบหก 8 กลุ่ม)", "distractors": ["32 บิต", "64 บิต", "256 บิต"],
        "explanation": "IPv4 มีขนาด 32 บิต ($2^{32} \\approx 4.3$ พันล้านหมายเลข) ส่วน IPv6 มีขนาด 128 บิต รองรับได้มหาศาล $2^{128}$ หมายเลข"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หมายเลข 'Loopback Address' ของ IPv6 สำหรับชี้มาที่เครื่องตนเองคือข้อใด?",
        "correct": "::1", "distractors": ["127.0.0.1", "fe80::1", "ff02::1"],
        "explanation": "IPv4 Loopback คือ 127.0.0.1 ส่วนในมาตรฐาน IPv6 ย่อเป็น ::1"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กลไก 'TCP Sliding Window' มีหน้าที่หลักเพื่อสิ่งใด?",
        "correct": "ควบคุมการไหลของข้อมูล (Flow Control) ป้องกันผู้ส่งส่งข้อมูลเร็วเกินกว่าผู้รับจะรับไหว", "distractors": ["ป้องกันการถูกดักฟังข้อมูลจากแฮกเกอร์", "เพิ่มความเร็วพัดลมในเราเตอร์", "เปลี่ยนสลับหน้าจอโปรแกรม"],
        "explanation": "Sliding Window ปรับขนาด Buffer ข้อมูลที่ส่งได้โดยไม่ต้องรอ Ack ทีละแพ็กเก็ต ช่วยปรับสมดุลความเร็วผู้ส่งและผู้รับ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอล 'NTP' (Network Time Protocol) มีไว้เพื่อวัตถุประสงค์ใดในระบบเครือข่าย?",
        "correct": "เทียบและปรับเวลาของนาฬิกาในระบบคอมพิวเตอร์ให้ตรงกันตามมาตรฐานสากล", "distractors": ["นับจำนวนผู้เข้าชมเว็บไซต์", "กำหนดความเร็วของพัดลมซีพียู", "ตั้งเวลาปิดเครื่องคอมพิวเตอร์"],
        "explanation": "NTP ใช้ซิงโครไนซ์เวลานาฬิกาของเครื่องในระบบเครือข่ายให้ตรงกันอย่างแม่นยำระดับมิลลิวินาที"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโปรโตคอลอีเมล 'IMAP' มีจุดเด่นเหนือกว่า 'POP3' อย่างไร?",
        "correct": "ซิงค์สถานะอีเมลและโฟลเดอร์ตรงกับเซิร์ฟเวอร์ เปิดอ่านได้หลายอุปกรณ์พร้อมกัน", "distractors": ["สามารถส่งข้อความได้โดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต", "มีขนาดไฟล์แนบไม่จำกัด", "ป้องกันสแปมได้ 100% เสมอ"],
        "explanation": "POP3 มักดาวน์โหลดเมลมาเก็บไว้ในเครื่องแล้วลบจากเซิร์ฟเวอร์ ส่วน IMAP ซิงค์ข้อมูลกับเซิร์ฟเวอร์แบบ Two-way"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การกำหนด 'Default Gateway' บนเครื่องคอมพิวเตอร์มีจุดประสงค์หลักเพื่ออะไร?",
        "correct": "ระบุ IP ของเราเตอร์ที่เป็นประตูทางออกส่งข้อมูลไปยังเครือข่ายภายนอกหรืออินเทอร์เน็ต", "distractors": ["ตั้งรหัสผ่านสำหรับเข้าเล่นเกม", "ระบุตำแหน่งที่ตั้งทางกายภาพของเครื่อง", "เพิ่มขนาดพื้นที่หน่วยความจำแรม"],
        "explanation": "เมื่อแพ็กเก็ตมีปลายทางอยู่นอก Subnet ของตนเอง ระบบจะส่งแพ็กเก็ตนั้นไปยัง Default Gateway (เราเตอร์) เสมอ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "พอร์ตมาตรฐานของบริการ 'MySQL Database' คือพอร์ตใด?",
        "correct": "พอร์ต 3306", "distractors": ["พอร์ต 5432 (PostgreSQL)", "พอร์ต 1433 (MS SQL)", "พอร์ต 27017 (MongoDB)"],
        "explanation": "MySQL / MariaDB ใช้พอร์ต 3306 เป็นค่าเริ่มต้นสำหรับการเชื่อมต่อฐานข้อมูล"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กลไก 'VLAN' (Virtual Local Area Network) บน Switch บริหารจัดการมีประโยชน์อย่างไร?",
        "correct": "แบ่งแยกวง Broadcast Domain ทางลอจิคัลบนสวิตช์ตัวเดียวกันเพื่อความปลอดภัยและประสิทธิภาพ", "distractors": ["เพิ่มความเร็วสายแลนเป็น 100 เท่า", "ขยายสัญญาณไฟบ้านให้จ่ายไฟได้มากขึ้น", "แปลงคอมพิวเตอร์ธรรมดาเป็นซูเปอร์คอมพิวเตอร์"],
        "explanation": "VLAN ช่วยแบ่งกลุ่มเครือข่ายออกจากกันเสมือนมีสวิตช์หลายตัว ช่วยลด Broadcast Traffic และเพิ่มความปลอดภัย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การทำงานของ 'Traceroute' ใช้คุณสมบัติใดของ IP Packet ในการตรวจจับ Router แต่ละ Hop?",
        "correct": "ค่อย ๆ เพิ่มค่า TTL เริ่มจาก 1 และดักรับข้อความ ICMP Time Exceeded กลับมา", "distractors": ["ส่งไวรัสไปทำลายเราเตอร์แต่ละตัว", "เปิดพอร์ต 80 ของทุกเราเตอร์ในโลก", "บันทึกเสียงสะท้อนของสัญญาณเคเบิล"],
        "explanation": "Traceroute ส่งแพ็กเก็ตที่ TTL=1, 2, 3... เพื่อให้เราเตอร์แต่ละจุดส่งข้อความ ICMP แจ้งกลับมาเมื่อ TTL หมดอายุ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำว่า 'Bandwidth' (แบนด์วิดท์) ในระบบเครือข่ายหมายถึงอะไร?",
        "correct": "ปริมาณข้อมูลสูงสุดที่สามารถส่งผ่านช่องทางสื่อสารได้ในหนึ่งหน่วยเวลา", "distractors": ["ระยะเวลาที่สัญญาณเดินทางไปและกลับ (Ping)", "น้ำหนักของสายเคเบิลเครือข่าย", "จำนวนเสาอากาศของเราเตอร์"],
        "explanation": "Bandwidth คือความกว้างของท่อส่งข้อมูล (ปริมาณต่อวินาที เช่น Gbps) ส่วน Latency คือความหน่วงเวลาในการเดินทาง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบเครือข่าย 'Jitter' หมายถึงค่าความผิดปกติของสิ่งใด?",
        "correct": "ความแปรปรวนหรือความไม่สม่ำเสมอของค่า Latency/Delay ในการรับส่งข้อมูล", "distractors": ["การรั่วไหลของกระแสไฟฟ้าในสายไฟ", "จำนวนไวรัสที่ตรวจพบในแต่ละวัน", "ความสว่างที่ไม่คงที่ของหน้าจอ"],
        "explanation": "Jitter คือความผันผวนของค่า Ping ซึ่งส่งผลกระทบอย่างมากต่อคุณภาพเสียง VoIP และการเล่นเกมออนไลน์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีแบบ 'SYN Flood Attack' บนโปรโตคอล TCP ใช้ประโยชน์จากช่องโหว่ใด?",
        "correct": "ส่งแพ็กเก็ต SYN ปลอมปริมาณมหาศาลโดยไม่ตอบกลับ ACK เพื่อจองคิว Half-open Connection จนล้น", "distractors": ["การขโมยสายเคเบิลอินเทอร์เน็ต", "การเดารหัสผ่านแอดมินด้วยพจนานุกรม", "การส่งอีเมลขยะจำนวนมาก"],
        "explanation": "SYN Flood ส่งคำขอเชื่อมต่อไปเรื่อย ๆ แต่ไม่ยอมส่ง ACK สุดท้าย ทำให้เซิร์ฟเวอร์เปิดรอจนคิวหน่วยความจำเต็มและค้าง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "การกำหนด 'Static IP' แตกต่างจาก 'Dynamic IP' อย่างไร?",
        "correct": "Static IP เป็นการตั้งค่าหมายเลข IP แบบคงที่ถาวร ไม่เปลี่ยนแปลงตามการแจกของ DHCP", "distractors": ["Static IP สามารถเปลี่ยนหมายเลขใหม่ทุก ๆ 5 นาที", "Dynamic IP ใช้ได้เฉพาะเครื่องที่ไม่มีหน้าจอ", "ทั้งสองแบบมีความเร็วเน็ตต่างกัน 10 เท่า"],
        "explanation": "Static IP กำหนดแบบเจาะจงคงที่ นิยมใช้กับ Server/Printer ส่วน Dynamic IP รับแจกแบบชั่วคราวจาก DHCP"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โปรโตคอลความปลอดภัย 'TLS 1.3' มีการพัฒนาเหนือกว่า TLS 1.2 ในเรื่องใด?",
        "correct": "ลดขั้นตอนการ Handshake เหลือเพียง 1-RTT (และรองรับ 0-RTT) พร้อมตัดอัลกอริทึมเข้ารหัสที่เก่าไม่ปลอดภัยออก", "distractors": ["ยกเลิกการเข้ารหัสข้อมูลทั้งหมดเพื่อให้เร็วขึ้น", "บังคับให้ผู้ใช้ทุกคนต้องจ่ายเงินรายเดือน", "ใช้งานได้เฉพาะบนระบบมือถือเท่านั้น"],
        "explanation": "TLS 1.3 ลดเวลา Handshake ลงครึ่งหนึ่งเพื่อความรวดเร็ว และยกเลิก Cipher Suites โบราณที่เปราะบางเพื่อความปลอดภัยสูงสุด"
    },

    # -------------------------------------------------------------
    # Category 4: Cybersecurity, Cryptography & Privacy (30 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การแฮชรหัสผ่านด้วยการใส่ 'Salt' มีวัตถุประสงค์หลักเพื่อป้องกันการโจมตีรูปแบบใด?",
        "correct": "การโจมตีแบบ Rainbow Table (ตารางแฮชคำตอบล่วงหน้า)", "distractors": ["การโจมตีด้วยไวรัสเรียกค่าไถ่", "การแอบตัดสายไฟเซิร์ฟเวอร์", "การโจมตีแบบ DDoS ถล่มเว็บ"],
        "explanation": "Salt คือสตริงสุ่มเฉพาะตัวที่นำมาต่อท้ายรหัสผ่านก่อนแฮช ทำให้ตาราง Rainbow Table สำเร็จรูปไม่สามารถเทียบถอดรหัสได้"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีเว็บแอปพลิเคชันแบบ 'Cross-Site Scripting' (XSS) มุ่งเป้ากระทำสิ่งใด?",
        "correct": "ฝังและรันโค้ด JavaScript อันตรายบนเบราว์เซอร์ของเหยื่อที่เข้ามาเปิดหน้าเว็บ", "distractors": ["ยิงคำสั่งลบฐานข้อมูลของเซิร์ฟเวอร์โดยตรง", "เจาะระบบไฟฟ้าของตึกสำนักงาน", "ทำให้พัดลมเคสของผู้ใช้หมุนเร็วเกินไป"],
        "explanation": "XSS แทรกสคริปต์อันตรายลงในหน้าเว็บเพื่อขโมย Cookie, Session Token หรือปลอมแปลงหน้าจอเข้าใช้งานของเหยื่อ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การป้องกันการโจมตีแบบ 'CSRF' (Cross-Site Request Forgery) นิยมใช้กลไกใด?",
        "correct": "การแนบ Anti-CSRF Token ลับเฉพาะในแบบฟอร์ม และตั้งค่าคุกกี้แบบ SameSite", "distractors": ["การปิดหน้าจอคอมพิวเตอร์หลังเลิกงาน", "การใช้แป้นพิมพ์ไร้สายเท่านั้น", "การเพิ่มขนาดแรมของเซิร์ฟเวอร์"],
        "explanation": "CSRF Token ป้องกันไม่ให้เว็บไซต์อันตรายสั่งให้เบราว์เซอร์ของเหยื่อส่งคำขอที่ไม่พึงประสงค์แทนตัวเหยื่อ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กลไกความปลอดภัย 'CORS' (Cross-Origin Resource Sharing) บนเว็บเบราว์เซอร์มีหน้าที่อะไร?",
        "correct": "ควบคุมและอนุญาตให้สคริปต์จากโดเมนหนึ่งสามารถร้องขอทรัพยากรข้ามไปยังอีกโดเมนหนึ่งได้หรือไม่", "distractors": ["แปลงโค้ดภาษาไทยเป็นภาษาอังกฤษ", "เพิ่มความเร็วการดาวน์โหลดวิดีโอ", "ป้องกันฝุ่นเกาะหน้าจอคอมพิวเตอร์"],
        "explanation": "CORS ใช้ HTTP Headers เพื่อให้เซิร์ฟเวอร์กำหนดว่า Domain ใดบ้างที่มีสิทธิ์เข้าถึง API ข้าม Origin ได้"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโครงสร้างโทเคนแบบ 'JWT' (JSON Web Token) ประกอบไปด้วย 3 ส่วนที่คั่นด้วยจุด (.) ข้อใดถูกต้อง?",
        "correct": "Header . Payload . Signature", "distractors": ["Username . Password . PIN", "Title . Body . Footer", "Source . Data . Checksum"],
        "explanation": "JWT ประกอบด้วย Header (อัลกอริทึม), Payload (ข้อมูล Claims) และ Signature (ลายเซ็นยืนยันความถูกต้อง)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีแบบ 'ARP Spoofing' (หรือ ARP Poisoning) ในเครือข่าย LAN นำไปสู่ภัยคุกคามใด?",
        "correct": "การโจมตีแบบ Man-in-the-Middle (ดักจับและแอบดูข้อมูลการสื่อสารในวง LAN)", "distractors": ["การทำลายชิปซีพียูให้ไหม้", "การเปลี่ยนรหัสผ่านอีเมลอัตโนมัติ", "การทำให้เราเตอร์ปิดการทำงาน"],
        "explanation": "ARP Spoofing หลอกเครื่องเหยื่อว่า MAC Address ของแฮกเกอร์คือเราเตอร์ ทำให้ข้อมูลทั้งหมดวิ่งผ่านเครื่องแฮกเกอร์ก่อน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "การหลอกลวงแบบ 'Spear Phishing' แตกต่างจาก 'Phishing' ทั่วไปอย่างไร?",
        "correct": "เจาะจงเป้าหมายบุคคลหรือองค์กรเฉพาะ โดยใช้ข้อมูลส่วนตัวที่น่าเชื่อถือมาหลอกลวง", "distractors": ["หลอกลวงผ่านข้อความ SMS บนมือถือเท่านั้น", "เป็นการโจมตีฮาร์ดแวร์โดยตรง", "ไม่มีการส่งลิงก์ปลอมใด ๆ ทั้งสิ้น"],
        "explanation": "Spear Phishing คือการปรับแต่งข้อความหลอกลวงให้ตรงกับเป้าหมายคนใดคนหนึ่งโดยเฉพาะ ทำให้เหยื่อหลงเชื่อได้ง่ายมาก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หลักการความปลอดภัยสมัยใหม่แบบ 'Zero Trust Architecture' มีแนวคิดหลักตรงกับข้อใด?",
        "correct": "'Never Trust, Always Verify' (ไม่เชื่อถือใครทั้งสิ้น ต้องตรวจสอบสิทธิ์ทุกครั้งอย่างต่อเนื่อง)", "distractors": ["เชื่อถืออุปกรณ์ทุกชิ้นที่เชื่อมต่อในเครือข่ายภายในองค์กร", "ไม่จำเป็นต้องตั้งรหัสผ่านหากต่อสายแลน", "ตั้งค่าให้เปิดเผยข้อมูลทั้งหมดเป็นสาธารณะ"],
        "explanation": "Zero Trust สมมติว่าเครือข่ายถูกเจาะอยู่ตลอดเวลา จึงต้องยืนยันตัวตน ตรวจสอบสิทธิ์ และเข้ารหัสทุกทราฟฟิกเสมอ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในวงการทดสอบเจาะระบบ (Penetration Testing) ทีม 'Red Team' มีบทบาทหน้าที่อะไร?",
        "correct": "สวมบทบาทเป็นแฮกเกอร์ฝ่ายรุกเพื่อค้นหาช่องโหว่และโจมตีระบบทดสอบ", "distractors": ["ฝ่ายดูแลและตั้งรับป้องกันระบบรักษาความปลอดภัย", "ฝ่ายเขียนเอกสารรายงานการเงิน", "ฝ่ายซ่อมแซมคอมพิวเตอร์ในสำนักงาน"],
        "explanation": "Red Team คือทีมฝ่ายรุก (Offensive) จำลองการโจมตีจริง ส่วน Blue Team คือทีมฝ่ายตั้งรับ (Defensive)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในระบบความปลอดภัยคอมพิวเตอร์ 'Honeypot' (โถน้ำผึ้ง) มีไว้เพื่อทำอะไร?",
        "correct": "ระบบล่อเป้าจำลองที่สร้างขึ้นมาเพื่อให้แฮกเกอร์เข้ามาโจมตีเพื่อศึกษารูปแบบพฤติกรรม", "distractors": ["โปรแกรมช่วยเพิ่มความเร็วอินเทอร์เน็ต", "รหัสผ่านลับที่ไม่มีใครสามารถเดาได้", "โปรแกรมล้างไฟล์ขยะในเครื่อง"],
        "explanation": "Honeypot วางกับดักระบบล่อใจให้แฮกเกอร์โจมตี ช่วยตรวจจับและเก็บข้อมูลเทคนิคการโจมตีก่อนระบบจริงจะถูกเจาะ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมการเข้ารหัสข้อมูลแบบสมมาตร (Symmetric Encryption) ที่เป็นมาตรฐานสากลและปลอดภัยสูงสุดคือข้อใด?",
        "correct": "AES (Advanced Encryption Standard เช่น AES-256)", "distractors": ["DES (Data Encryption Standard)", "MD5", "Base64"],
        "explanation": "AES-256 เป็นมาตรฐานการเข้ารหัสแบบ Symmetric Block Cipher ที่รัฐบาลและองค์กรชั้นนำทั่วโลกใช้งานอย่างปลอดภัย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมการแฮชข้อความแบบ 'MD5' และ 'SHA-1' ในปัจจุบันไม่แนะนำให้ใช้ในงานความปลอดภัยเพราะเหตุใด?",
        "correct": "เกิดปัญหา Hash Collision (ข้อมูลต่างกันแต่ได้ค่าแฮชเดียวกัน) ได้ง่าย", "distractors": ["ประมวลผลช้าเกินไปสำหรับคอมพิวเตอร์รุ่นใหม่", "สามารถแปลงกลับเป็นไฟล์วิดีโอได้", "กินไฟสูงเกินมาตรฐานสากล"],
        "explanation": "MD5 และ SHA-1 มีช่องโหว่ทางคณิตศาสตร์ที่ทำให้นักวิจัยสามารถสร้าง Collision ได้สำเร็จ จึงถูกยกเลิกการใช้งานด้านความปลอดภัย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ฟังก์ชันแฮชรหัสผ่านอย่าง 'bcrypt' หรือ 'Argon2' ดีกว่า SHA-256 ธรรมดาในการเก็บรหัสผ่านอย่างไร?",
        "correct": "สามารถปรับค่า Work Factor (Cost) ให้คำนวณช้าลง เพื่อป้องกันการ Brute-force ด้วย GPU/ASIC", "distractors": ["ทำให้รหัสผ่านสั้นลงเหลือ 4 ตัวอักษร", "กู้คืนรหัสผ่านกลับมาได้เมื่อลืม", "บีบอัดไฟล์ฐานข้อมูลให้เล็กลง"],
        "explanation": "Slow Hashing Functions อย่าง Argon2 และ bcrypt ออกแบบมาให้กินเวลาและ Memory สูง ทำให้การสุ่มถอดรหัสผ่านด้วย GPU ช้าลงมหาศาล"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "การเข้ารหัสแบบ 'End-to-End Encryption' (E2EE) ในแอปแชทมีความหมายว่าอย่างไร?",
        "correct": "มีเพียงผู้ส่งและผู้รับปลายทางเท่านั้นที่ถอดรหัสอ่านข้อความได้ แม้แต่ผู้ให้บริการเซิร์ฟเวอร์ก็อ่านไม่ได้", "distractors": ["ข้อความจะถูกส่งไปให้อ่านเฉพาะช่วงปลายสัปดาห์", "ข้อความจะถูกบันทึกเป็นไฟล์เสียงทั้งหมด", "ข้อความจะถูกลบหลังจากส่งไป 1 วินาทีเสมอ"],
        "explanation": "E2EE เข้ารหัสที่เครื่องผู้ส่งและถอดรหัสที่เครื่องผู้รับเท่านั้น เซิร์ฟเวอร์ทำหน้าที่แค่ส่งผ่านข้อมูลโดยถอดรหัสไม่ได้"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีแบบ 'Directory Traversal' (Path Traversal) มีลักษณะพฤติกรรมอย่างไร?",
        "correct": "ใส่สัญลักษณ์เช่น '../' ใน Input เพื่อแอบเข้าถึงไฟล์สำคัญนอกโฟลเดอร์ที่กำหนด (เช่น /etc/passwd)", "distractors": ["สร้างโฟลเดอร์ใหม่จนฮาร์ดดิสก์เต็ม", "ลบประวัติการเข้าใช้งานทั้งหมดทิ้ง", "ส่งไวรัสผ่านสายไฟบ้าน"],
        "explanation": "Path Traversal หลอกพาธไฟล์ด้วย Dot-Dot-Slash เพื่อย้อนกลับไปอ่านไฟล์ระบบที่ไม่ได้อนุญาตให้สาธารณะเข้าถึง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "คุณสมบัติ 'HTTP-Only' บนคุกกี้ (Cookie) ช่วยป้องกันภัยคุกคามข้อใด?",
        "correct": "ป้องกันไม่ให้โค้ด JavaScript (XSS) สามารถเข้าถึงและขโมยค่า Cookie ได้", "distractors": ["ป้องกันไม่ให้คอมพิวเตอร์ต่อสายแลน", "ป้องกันไม่ให้เปิดเว็บไซต์ผ่าน HTTPS", "ป้องกันไม่ให้เบราว์เซอร์บันทึกประวัติ"],
        "explanation": "HttpOnly Flag สั่งให้เบราว์เซอร์ห้ามไม่ให้ document.cookie อ่านค่าคุกกี้นี้ได้ ช่วยป้องกันการขโมย Session ID ผ่าน XSS"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "คุณสมบัติ 'SameSite=Strict' บนคุกกี้มีประโยชน์สำคัญที่สุดคืออะไร?",
        "correct": "เบราว์เซอร์จะไม่ส่งคุกกี้นี้ไปกับคำขอที่ข้ามมาจากเว็บไซต์อื่น ช่วยป้องกัน CSRF", "distractors": ["ทำให้สามารถเปิดเว็บได้เร็วขึ้น 10 เท่า", "ล็อกไม่ให้ผู้ใช้กดออกจากระบบ", "ลบคุกกี้ทิ้งทันทีที่ปิดหน้าต่าง"],
        "explanation": "SameSite=Strict บล็อกการส่งคุกกี้ในทราฟฟิก Cross-Site Request ทุกกรณี ช่วยตัดช่องโหว่ CSRF ได้อย่างสมบูรณ์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในการแลกเปลี่ยนกุญแจเข้ารหัสลับผ่านเครือข่ายสาธารณะ อัลกอริทึมใดที่ได้รับความนิยมสูงสุด?",
        "correct": "Diffie-Hellman Key Exchange", "distractors": ["Bubble Sort", "Dijkstra Algorithm", "Binary Search"],
        "explanation": "Diffie-Hellman ช่วยให้ 2 ฝั่งสามารถสร้าง Shared Secret Key ร่วมกันได้อย่างปลอดภัยผ่านช่องทางที่ไม่ปลอดภัย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ข้อใด 'ไม่ใช่' หนึ่งในสามเสาหลักของความมั่นคงปลอดภัยสารสนเทศ (CIA Triad)?",
        "correct": "Convenience (ความสะดวกสบายในการใช้งาน)", "distractors": ["Confidentiality (การรักษาความลับ)", "Integrity (ความถูกต้องสมบูรณ์)", "Availability (ความพร้อมใช้งาน)"],
        "explanation": "CIA Triad คือ: Confidentiality (ความลับ), Integrity (ความสมบูรณ์ถูกต้อง), Availability (ความพร้อมใช้งาน)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "มัลแวร์ประเภท 'Keylogger' มีรูปแบบการขโมยข้อมูลอย่างไร?",
        "correct": "แอบบันทึกทุกปุ่มบนแป้นพิมพ์ที่ผู้ใช้งานกด เพื่อดักจับรหัสผ่านและข้อมูลส่วนตัว", "distractors": ["ล็อกไม่ให้ผู้ใช้งานกดแป้นพิมพ์ได้", "ลบปุ่มลัดบนคีย์บอร์ดทิ้งทั้งหมด", "ทำให้แป้นพิมพ์เปลี่ยนเป็นภาษาต่างดาว"],
        "explanation": "Keylogger บันทึก Keystrokes ทั้งหมดส่งกลับไปให้แฮกเกอร์ ทำให้ได้ทั้งชื่อผู้ใช้ รหัสผ่าน และข้อความแชท"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีแบบ 'Session Hijacking' (การขโมยเซสชัน) มักเกิดจากการขโมยสิ่งใดของเหยื่อ?",
        "correct": "Session ID / Session Token ที่เก็บอยู่ในคุกกี้ของเบราว์เซอร์", "distractors": ["สายไฟและปลั๊กไฟของเครื่องคอมพิวเตอร์", "หมายเลขซีเรียลของการ์ดจอ", "ภาพหน้าจอเดสก์ท็อป"],
        "explanation": "เมื่อแฮกเกอร์ได้ Session Token ของเหยื่อ ก็จะสามารถสวมรอยล็อกอินเข้าสู่ระบบได้ทันทีโดยไม่ต้องรู้รหัสผ่านจริง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ใบรับรองความปลอดภัย 'SSL/TLS Certificate' บนเว็บไซต์ ออกและรับรองโดยหน่วยงานใด?",
        "correct": "Certificate Authority (CA เช่น Let's Encrypt, DigiCert)", "distractors": ["ผู้ผลิตการ์ดจอคอมพิวเตอร์", "บริษัทผู้ให้บริการไฟฟ้า", "ผู้เล่นเกมออนไลน์"],
        "explanation": "CA ทำหน้าที่ตรวจสอบความถูกต้องและออก Digital Certificate เพื่อยืนยันตัวตนของโดเมนบนอินเทอร์เน็ต"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิคการโจมตีแบบ 'Replay Attack' มีลักษณะการทำงานอย่างไร?",
        "correct": "ดักจับแพ็กเก็ตข้อมูลยืนยันตัวตนที่ส่งผ่านเครือข่าย แล้วส่งซ้ำอีกครั้งเพื่อสวมรอย", "distractors": ["เปิดวิดีโอซ้ำ ๆ จนเซิร์ฟเวอร์ค้าง", "การกดรีเฟรชหน้าเว็บหลายครั้ง", "การบันทึกเสียงลำโพงในห้อง"],
        "explanation": "Replay Attack ดักจับข้อความที่ถูกต้องแล้วส่งซ้ำ (ป้องกันได้โดยใช้ Nonce, Timestamp หรือ One-Time Tokens)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การเข้ารหัสลับแบบ 'Homomorphic Encryption' มีความสามารถพิเศษสุดยอดข้อใด?",
        "correct": "สามารถประมวลผลและคำนวณข้อมูลได้โดยตรงทั้ง ๆ ที่ข้อมูลยังคงถูกเข้ารหัสอยู่", "distractors": ["สามารถถอดรหัสผ่านได้ทุกรหัสในโลกใน 1 วินาที", "ทำให้ไฟล์รูปภาพกลายเป็นไฟล์เพลง", "ไม่ต้องใช้ซีพียูในการประมวลผล"],
        "explanation": "Homomorphic Encryption ช่วยให้สามารถส่งข้อมูลขึ้น Cloud เพื่อประมวลผลได้โดยที่ Cloud Provider ไม่เห็นข้อมูลจริง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การโจมตีแบบ 'Typosquatting' มีลักษณะการหลอกลวงอย่างไร?",
        "correct": "จดโดเมนที่สะกดผิดเล็กน้อยคล้ายเว็บดัง (เช่น goggle.com) เพื่อหลอกผู้ใช้ที่พิมพ์ผิด", "distractors": ["การพิมพ์คีย์บอร์ดเสียงดังเกินไป", "การพิมพ์ภาษาไทยสลับกับภาษาอังกฤษ", "การตั้งรหัสผ่านด้วยตัวพิมพ์เล็กทั้งหมด"],
        "explanation": "Typosquatting ฉวยโอกาสจากผู้ใช้ที่พิมพ์ URL ผิด เพื่อพาไปยังเว็บ Phishing หรือหน้าติดมัลแวร์"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "กระบวนการ 'Sanitization' ในการพัฒนาเว็บแอปพลิเคชันมีไว้เพื่ออะไร?",
        "correct": "การล้างและแปลงอักขระพิเศษใน Input เพื่อป้องกันการรันคำสั่งอันตราย (เช่น SQLi, XSS)", "distractors": ["การเช็ดทำความสะอาดหน้าจอคอมพิวเตอร์", "การปิดเครื่องคอมพิวเตอร์หลังใช้งาน", "การลบไฟล์เพลงที่ไม่ได้ฟัง"],
        "explanation": "Data Sanitization ทำความสะอาดข้อมูลนำเข้า ตัดแท็ก HTML/JS หรือ Escape อักขระคำสั่ง SQL เพื่อความปลอดภัย"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "การหลอกลวงทางโทรศัพท์เพื่อหลอกเอาข้อมูลทางการเงินและรหัส OTP เรียกว่าอะไร?",
        "correct": "Vishing (Voice Phishing)", "distractors": ["Smishing", "Pharming", "Defacement"],
        "explanation": "Vishing คือ Voice Phishing (หลอกทางเสียง/โทรศัพท์) ส่วน Smishing คือ SMS Phishing (หลอกทางข้อความสั้น)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ช่องโหว่ความปลอดภัย 'Insecure Direct Object References' (IDOR) เกิดจากสาเหตุใด?",
        "correct": "ระบบเปิดให้เข้าถึงข้อมูลโดยตรงผ่าน ID ใน URL โดยไม่มีการตรวจสอบสิทธิ์การเป็นเจ้าของ", "distractors": ["สายแลนชำรุดเสียหาย", "การใช้ตัวอักษรภาษาอังกฤษในรหัสผ่าน", "การเปิดโปรแกรมมากเกินไป"],
        "explanation": "IDOR เกิดเมื่อเปลี่ยนตัวเลข ID ใน URL (เช่น /api/user/123 เป็น /api/user/124) แล้วระบบดันแสดงข้อมูลของผู้อื่นออกมา"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "มาตรฐานความปลอดภัยข้อมูลบัตรชำระเงินสำหรับร้านค้าออนไลน์มีชื่อย่อว่าอะไร?",
        "correct": "PCI-DSS", "distractors": ["ISO-9001", "IEEE-802", "W3C-HTML"],
        "explanation": "PCI-DSS (Payment Card Industry Data Security Standard) เป็นมาตรฐานความปลอดภัยเข้มงวดสำหรับการจัดเก็บและส่งข้อมูลบัตรเครดิต"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ภัยคุกคาม 'Ransomware-as-a-Service' (RaaS) มีรูปแบบธุรกิจมืดอย่างไร?",
        "correct": "ผู้พัฒนามัลแวร์เปิดเช่าซอฟต์แวร์เรียกค่าไถ่ให้พันธมิตรนำไปโจมตีแล้วแบ่งผลกำไรกัน", "distractors": ["บริการกู้คืนไฟล์ที่ถูกล็อกฟรีโดยไม่คิดเงิน", "การขายชิ้นส่วนคอมพิวเตอร์มือสอง", "บริการสอนเขียนโปรแกรมออนไลน์"],
        "explanation": "RaaS เป็นโมเดลธุรกิจอาชญากรรมไซเบอร์ที่เจ้าของ Ransomware ให้ผู้ร่วมขบวนการ (Affiliates) นำมัลแวร์ไปปล่อยและแบ่งค่าไถ่กัน"
    },

    # -------------------------------------------------------------
    # Category 5: Algorithms, Data Structures & Logic (35 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูลแบบ 'Binary Search Tree' (BST) ในกรณีที่แย่ที่สุด (Worst Case ข้อมูลเรียงลำดับมา) จะมีเวลาค้นหาเท่าใด?",
        "correct": "O(n) เสื่อมสภาพกลายเป็น Linked List", "distractors": ["O(log n)", "O(1)", "O(n log n)"],
        "explanation": "หากแทรกข้อมูลที่เรียงลำดับแล้วเข้าไปใน Unbalanced BST ต้นไม้จะเอียงข้างเดียวและมีความสูงเท่ากับ n ส่งผลให้ค้นหาช้า O(n)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างต้นไม้แบบ 'AVL Tree' หรือ 'Red-Black Tree' พัฒนาขึ้นมาเพื่อแก้ปัญหาใดของ BST?",
        "correct": "การปรับสมดุลต้นไม้อัตโนมัติ (Self-Balancing) เพื่อรักษาความเร็วค้นหา O(log n) เสมอ", "distractors": ["เพิ่มความจุของฮาร์ดดิสก์ในการบันทึก", "ลดการใช้พลังงานไฟฟ้าของซีพียู", "ทำให้ต้นไม้มีใบเป็นสีเขียว"],
        "explanation": "Self-Balancing Trees จะหมุนต้นไม้ (Rotation) อัตโนมัติเพื่อควบคุมความสูงให้อยู่ในระดับ $O(\\log n)$ เสมอ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูล 'Min-Heap' มีคุณสมบัติสำคัญอย่างไรที่ Root Node?",
        "correct": "โหนดรากจะมีค่าน้อยที่สุดเสมอเมื่อเทียบกับลูกหลานทั้งหมด", "distractors": ["โหนดรากจะมีค่ามากที่สุดเสมอ", "โหนดรากจะเก็บค่าเฉลี่ยของข้อมูลทั้งหมด", "โหนดรากจะว่างเปล่าไม่มีข้อมูล"],
        "explanation": "Min-Heap กำหนดให้ Parent Node มีค่าน้อยกว่าหรือเท่ากับ Child Nodes เสมอ ทำให้ดึงค่าต่ำสุดออกมาได้เร็วใน $O(1)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมท่องกราฟแบบ 'Breadth-First Search' (BFS) ใช้โครงสร้างข้อมูลใดในการจัดการลำดับการเข้าชม?",
        "correct": "คิว (Queue)", "distractors": ["สแต็ก (Stack)", "ทรี (Tree)", "ไบนารีฮีป (Binary Heap)"],
        "explanation": "BFS สำรวจตามแนวกว้างทีละระดับ (Level-by-Level) จึงต้องใช้ Queue (FIFO) ในการจัดคิวโหนดที่ต้องเข้าชม"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมท่องกราฟแบบ 'Depth-First Search' (DFS) สัมพันธ์กับโครงสร้างข้อมูลหรือการทำงานแบบใด?",
        "correct": "สแต็ก (Stack) หรือการเรียกใช้ Recursion", "distractors": ["คิว (Queue)", "แถวลำดับสองมิติ", "แฮชเทเบิล"],
        "explanation": "DFS สำรวจลึกไปตามกิ่งจนสุดทางโดยใช้ Call Stack (Recursion) หรือ Explicit Stack (LIFO)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมของ 'Dijkstra' มีข้อจำกัดสำคัญที่ไม่สามารถทำงานได้อย่างถูกต้องในกรณีใด?",
        "correct": "กราฟที่มีค่าน้ำหนักของเส้นเชื่อมเป็นค่าติดลบ (Negative Edge Weights)", "distractors": ["กราฟที่มีจำนวนโหนดมากกว่า 10 โหนด", "กราฟที่ไม่มีเส้นทางวนกลับ", "กราฟที่มีโหนดเชื่อมต่อกันครบทุกโหนด"],
        "explanation": "Dijkstra ใช้หลักการ Greedy จึงไม่สามารถจัดการกับ Negative Weights ได้ (ถ้ามีติดลบต้องใช้ Bellman-Ford Algorithm)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมหาต้นไม้ทอดข้ามขั้นต่ำ 'Kruskal's Algorithm' ใช้โครงสร้างข้อมูลใดในการตรวจจับการเกิดวงวน (Cycle)?",
        "correct": "Disjoint Set Union (DSU / Union-Find)", "distractors": ["Binary Search Tree", "Linked List", "Hash Map"],
        "explanation": "Kruskal จัดเรียงน้ำหนักเส้นเชื่อมและใช้ DSU ในการตรวจสอบว่าโหนดทั้งสองอยู่ในกลุ่มเดียวกันหรือไม่เพื่อกันการเกิด Loop"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิคการเขียนโปรแกรมแบบพลวัต (Dynamic Programming) แบบ 'Memoization' มีแนวคิดหลักอย่างไร?",
        "correct": "การแก้ปัญหาแบบบนลงล่าง (Top-Down) โดยจดจำผลลัพธ์ของปัญหาย่อยที่เคยคำนวณแล้วไว้ในตาราง/แคช", "distractors": ["การคำนวณผลลัพธ์ใหม่ทั้งหมดทุกครั้งที่เรียกใช้งาน", "การแก้ปัญหาแบบล่างขึ้นบนโดยไม่ใช้ฟังก์ชันซ้ำ", "การสุ่มตัวเลขเพื่อหาคำตอบที่ใกล้เคียงที่สุด"],
        "explanation": "Memoization จดจำคำตอบของ Subproblems ที่เคยคิดแล้วผ่าน Recursion + Cache ช่วยลดเวลาจาก Exponential เป็น Linear/Polynomial"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในภาษาโปรแกรมส่วนใหญ่ ผลลัพธ์ของการคำนวณ '0.1 + 0.2 == 0.3' มักคืนค่า 'False' เพราะสาเหตุใด?",
        "correct": "ข้อจำกัดการแทนจำนวนจริงทศนิยมในระบบเลขฐานสองตามมาตรฐาน IEEE 754 (Rounding Error)", "distractors": ["คอมพิวเตอร์ไม่รู้จักเครื่องหมายบวก", "ตัวเลข 0.3 เป็นจำนวนเฉพาะที่ไม่สามารถเปรียบเทียบได้", "ระบบปฏิบัติการแอบเปลี่ยนค่าตัวเลข"],
        "explanation": "เลขฐานสิบ 0.1 และ 0.2 เมื่อแปลงเป็นเลขฐานสองจะเป็นทศนิยมไม่รู้จบ ทำให้เกิดความคลาดเคลื่อนเล็กน้อย (0.30000000000000004)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การแทนจำนวนเต็มลบในคอมพิวเตอร์ด้วยระบบ 'Two's Complement' ของเลขฐานสอง 8 บิต '00000101' (+5) คือข้อใด?",
        "correct": "11111011 (-5)", "distractors": ["11111010", "10000101", "00000101"],
        "explanation": "Two's Complement: สลับ 0 เป็น 1 และ 1 เป็น 0 (ได้ 11111010) แล้วบวกเพิ่มด้วย 1 จะได้ 11111011"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ตัวดำเนินการระดับบิต (Bitwise XOR : ^) มีคุณสมบัติพิเศษข้อใดที่เป็นจริงเสมอ?",
        "correct": "x ^ x = 0 และ x ^ 0 = x", "distractors": ["x ^ x = x", "x ^ 0 = 0", "x ^ 1 = 0 เสมอ"],
        "explanation": "Bitwise XOR คืนค่า 0 เมื่อบิตเหมือนกัน และคืนค่า 1 เมื่อบิตต่างกัน จึงนำมาใช้หาตัวเลขที่ไม่ซ้ำคู่ใน Array ได้อย่างรวดเร็ว"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "การเลื่อนบิตไปทางซ้าย 1 ตำแหน่ง (Bitwise Left Shift : x << 1) ให้ผลลัพธ์ทางคณิตศาสตร์เทียบเท่ากับสิ่งใด?",
        "correct": "การคูณค่า x ด้วย 2", "distractors": ["การหารค่า x ด้วย 2", "การยกกำลังสองค่า x", "การบวกค่า x เพิ่มด้วย 1"],
        "explanation": "การเลื่อนบิตไปทางซ้าย $x \\ll n$ เทียบเท่ากับการคูณด้วย $2^n$ (ส่วนการเลื่อนขวา $x \\gg n$ เทียบเท่ากับการหารด้วย $2^n$ ปัดเศษลง)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในการจัดการข้อมูลชนกัน (Collision Resolution) ของ Hash Table วิธี 'Chaining' จัดการอย่างไร?",
        "correct": "เก็บข้อมูลที่ตกในช่องเดียวกันไว้ใน Linked List หรือต้นไม้ภายใน Bucket นั้น", "distractors": ["ลบข้อมูลตัวเก่าทิ้งทันทีเมื่อมีตัวใหม่เข้ามา", "ขยายขนาดของตารางเป็น 10 เท่าทันที", "ปฏิเสธไม่รับข้อมูลใหม่"],
        "explanation": "Separate Chaining อนุญาตให้แต่ละ Bucket ใน Hash Table เก็บเป็น Linked List เพื่อรองรับหลาย Element ที่ได้ Hash Index เดียวกัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การจัดเรียงข้อมูลแบบ 'Counting Sort' มีประสิทธิภาพ Time Complexity ดีถึง $O(n + k)$ ภายใต้เงื่อนไขใด?",
        "correct": "ข้อมูลนำเข้าเป็นจำนวนเต็มที่มีช่วงของค่า (Range k) ไม่กว้างจนเกินไป", "distractors": ["ข้อมูลต้องเป็นข้อความยาวเกิน 1,000 ตัวอักษร", "ข้อมูลต้องถูกจัดเรียงมาแล้วล่วงหน้า", "ข้อมูลต้องเป็นจำนวนจริงทศนิยมเท่านั้น"],
        "explanation": "Counting Sort ไม่ใช้การเปรียบเทียบ (Non-comparison Sort) จึงเร็วกว่า $O(n \\log n)$ เมื่อ Range ข้อมูล $k$ มีขนาดเล็กพอเหมาะ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิค 'Sliding Window' นิยมนำมาใช้แก้โจทย์ปัญหาอัลกอริทึมประเภทใดได้อย่างมีประสิทธิภาพ?",
        "correct": "การหาผลรวมหรือคุณสมบัติของ Subarray/Substring ที่มีขนาดต่อเนื่องกัน", "distractors": ["การเรียงลำดับไฟล์ในฮาร์ดดิสก์", "การค้นหาข้อผิดพลาดของสายไฟ", "การเปิดหน้าต่างแอปพลิเคชันพร้อมกันหลายหน้าต่าง"],
        "explanation": "Sliding Window ช่วยลด Time Complexity จาก $O(n^2)$ เหลือ $O(n)$ ในการคำนวณข้อมูลช่วงต่อเนื่องโดยการเลื่อนขอบเข้าออก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ปัญหาความยากเชิงคำนวณระดับ 'NP-Complete' มีลักษณะสำคัญอย่างไร?",
        "correct": "ยังไม่มีอัลกอริทึม Polynomial-time ที่แก้ปัญหาได้ในเวลาเร็ว แต่สามารถตรวจสอบความถูกต้องของคำตอบได้เร็วใน P-time", "distractors": ["ปัญหาที่ไม่สามารถใช้คอมพิวเตอร์เขียนโปรแกรมได้เลย", "ปัญหาที่ใช้เวลาคำนวณเท่ากับ O(1) เสมอ", "ปัญหาที่แก้ได้เฉพาะบนคอมพิวเตอร์ควอนตัมเท่านั้น"],
        "explanation": "ปัญหา NP-Complete (เช่น Traveling Salesperson, Knapsack) ยากที่จะหาคำตอบที่ดีที่สุดใน Polynomial Time แต่ตรวจคำตอบได้ใน $O(n^k)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "โครงสร้างข้อมูลแบบ 'Linked List' มีข้อได้เปรียบเหนือ 'Array' ปกติในเรื่องใด?",
        "correct": "การแทรกหรือลบโหนดที่หัวหรือตำแหน่งที่รู้พอยน์เตอร์ทำได้เร็ว $O(1)$ โดยไม่ต้องขยับเลื่อนข้อมูลทั้งแถว", "distractors": ["สามารถเข้าถึงข้อมูลตำแหน่งใด ๆ (Random Access) ได้เร็วใน $O(1)$", "ใช้เนื้อที่หน่วยความจำน้อยกว่า Array", "ค้นหาข้อมูลได้เร็วกว่า Array เสมอ"],
        "explanation": "Linked List ปรับเปลี่ยนขนาดได้ยืดหยุ่นและแทรกโหนดได้ทันทีใน $O(1)$ แต่เข้าถึงแบบระบุดัชนีต้องวิ่งไล่หา $O(n)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูลแบบ 'Doubly Linked List' แตกต่างจาก 'Singly Linked List' อย่างไร?",
        "correct": "แต่ละโหนดจะเก็บพอยน์เตอร์ชี้ไปทั้งโหนดถัดไป (Next) และโหนดก่อนหน้า (Prev)", "distractors": ["สามารถเก็บข้อมูลได้เฉพาะตัวเลขสองหลัก", "ใช้เนื้อที่หน่วยความจำน้อยกว่าครึ่งหนึ่ง", "สามารถทำงานได้โดยไม่ต้องใช้พอยน์เตอร์"],
        "explanation": "Doubly Linked List มี Pointer 2 ตัว (Next และ Prev) ทำให้ท่องข้อมูลย้อนกลับและลบโหนดปัจจุบันได้สะดวกขึ้น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมการบีบอัดข้อมูลแบบ 'Huffman Coding' สร้างรหัสบิตโดยอาศัยหลักการใด?",
        "correct": "ตัวอักษรที่ปรากฏบ่อยที่สุดจะถูกแทนที่ด้วยรหัสบิตที่สั้นที่สุด (Variable-length Prefix Codes)", "distractors": ["แทนที่ทุกตัวอักษรด้วยความยาว 8 บิตเท่ากันเสมอ", "ลบตัวสระภาษาอังกฤษทิ้งทั้งหมด", "แปลงข้อความเป็นไฟล์รูปภาพ"],
        "explanation": "Huffman Coding สร้าง Optimal Prefix Tree ตามความถี่ เพื่อให้ตัวอักษรที่ใช้บ่อยใช้จำนวนบิตน้อยที่สุดในการจัดเก็บ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูล 'Trie' (Prefix Tree) เหมาะสำหรับนำไปประยุกต์ใช้งานด้านใดมากที่สุด?",
        "correct": "ระบบเติมคำอัตโนมัติ (Autocomplete) และการค้นหาพจนานุกรมคำศัพท์", "distractors": ["การคำนวณดอกเบี้ยธนาคาร", "การตัดต่อเสียงเพลง", "การควบคุมอุณหภูมิซีพียู"],
        "explanation": "Trie จัดเก็บตัวอักษรตามลำดับเส้นทาง ทำให้ค้นหาคำและคำที่มีคำนำหน้า (Prefix) ร่วมกันได้เร็วใน $O(L)$ โดย $L$ คือความยาวคำ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในการเขียนโปรแกรม ฟังก์ชันแบบ 'Pure Function' มีคุณสมบัติสำคัญข้อใด?",
        "correct": "เมื่อให้อินพุตเดิมจะได้ผลลัพธ์เดิมเสมอ และไม่มีผลข้างเคียง (No Side Effects) ออกนอกฟังก์ชัน", "distractors": ["ฟังก์ชันที่เขียนโดยไม่ใช้ตัวแปรใด ๆ เลย", "ฟังก์ชันที่สามารถรันได้เฉพาะบนระบบปฏิบัติการ Linux", "ฟังก์ชันที่ทำงานได้เร็วที่สุดในโลก"],
        "explanation": "Pure Function ไม่แก้ไขตัวแปรภายนอก ไม่ยุ่งกับ I/O ทำให้อ่าน เข้าใจ ทดสอบ และทำ Unit Test ได้ง่ายและแม่นยำ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หลักการทางตรรกศาสตร์ 'De Morgan's Laws' ข้อใดเทียบเท่ากับคำสั่ง 'not (A and B)'?",
        "correct": "(not A) or (not B)", "distractors": ["(not A) and (not B)", "A and (not B)", "(not A) and B"],
        "explanation": "กฎของเดอมอร์แกน: $\\neg (A \\land B) \\iff \\neg A \\lor \\neg B$ และ $\\neg (A \\lor B) \\iff \\neg A \\land \\neg B$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในการเขียนโปรแกรมแบบอะซิงโครนัส 'Race Condition' เกิดขึ้นได้อย่างไร?",
        "correct": "หลายเธรดพยายามเข้าถึงและแก้ไขข้อมูลเดียวกันพร้อมกันโดยผลลัพธ์ขึ้นอยู่กับลำดับการทำงานที่ไม่แน่นอน", "distractors": ["การแข่งขันเขียนโค้ดจับเวลา", "การดาวน์โหลดโปรแกรมแข่งกับเพื่อน", "พัดลมสองตัวหมุนด้วยความเร็วไม่เท่ากัน"],
        "explanation": "Race Condition เกิดขึ้นใน Critical Section เมื่อไม่มีการ Sync/Locking ทำให้ข้อมูลปลายทางคำนวณผิดเพี้ยน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "โครงสร้างข้อมูลแบบ 'Set' (เซต) ในภาษาอย่าง Python แตกต่างจาก 'List' อย่างไร?",
        "correct": "สมาชิกใน Set จะไม่ซ้ำกันอย่างเด็ดขาด และไม่มีลำดับดัชนีแน่นอน", "distractors": ["Set สามารถเก็บข้อมูลได้เฉพาะตัวเลขจำนวนเต็ม", "List ไม่สามารถเพิ่มข้อมูลใหม่ได้", "Set ใช้พื้นที่หน่วยความจำน้อยกว่า List 100 เท่า"],
        "explanation": "Set เก็บเฉพาะ Unique Values และใช้ Hash Table ภายใน ทำให้ตรวจสอบการมีอยู่ (x in set) ได้เร็วระดับ $O(1)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในภาษาโปรแกรม รูปแบบฟังก์ชัน 'Higher-Order Function' หมายถึงข้อใด?",
        "correct": "ฟังก์ชันที่สามารถรับฟังก์ชันอื่นเป็นพารามิเตอร์ หรือส่งฟังก์ชันกลับออกมาเป็นผลลัพธ์ได้", "distractors": ["ฟังก์ชันที่มีความยาวโค้ดเกิน 1,000 บรรทัด", "ฟังก์ชันที่ต้องรันด้วยสิทธิ์ของผู้ดูแลระบบสูงสุด", "ฟังก์ชันที่เขียนอยู่ด้านบนสุดของไฟล์"],
        "explanation": "Higher-Order Functions (เช่น map, filter, reduce) ปฏิบัติต่อฟังก์ชันเป็น First-Class Citizens"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "รูปแบบการประมวลผล 'Tail Call Optimization' (TCO) ช่วยป้องกันปัญหาใดในการใช้ Recursion?",
        "correct": "ช่วยไม่ให้เกิด Stack Overflow โดยนำ Stack Frame เดิมกลับมาใช้ซ้ำสำหรับคำสั่งสุดท้าย", "distractors": ["ช่วยป้องกันไม่ให้ฮาร์ดดิสก์เต็ม", "ช่วยป้องกันไม่ให้เครื่องร้อนเกินไป", "ช่วยให้หน้าจอแสดงผลได้เร็วขึ้น"],
        "explanation": "เมื่อการเรียก Recursion อยู่บรรทัดสุดท้าย คอมไพเลอร์ที่รองรับ TCO จะ Reuse Stack Frame เดิมแทนที่จะสร้างใหม่"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ตัวแปรชนิด 'Immutable' (เช่น tuple, str ใน Python) มีความหมายว่าอย่างไร?",
        "correct": "อ็อบเจกต์ที่ไม่สามารถแก้ไขเปลี่ยนแปลงค่าภายในหลังจากสร้างเสร็จแล้ว", "distractors": ["ตัวแปรที่สามารถเปลี่ยนชื่อได้ตลอดเวลา", "ตัวแปรที่ไม่สามารถลบออกจากหน่วยความจำได้", "ตัวแปรที่สามารถเก็บข้อมูลได้ไม่จำกัดขนาด"],
        "explanation": "Immutable Object เมื่อถูกสร้างแล้วจะไม่สามารถแก้ไขค่าเดิมได้ หากมีการแก้ไขจะเป็นการสร้างอ็อบเจกต์ใหม่ใน RAM"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึม 'Topological Sort' สามารถทำงานได้เฉพาะกับกราฟประเภทใด?",
        "correct": "DAG (Directed Acyclic Graph กราฟระบุทิศทางที่ไม่มีวงวน)", "distractors": ["กราฟแบบไม่ระบุทิศทางที่มีวงวน", "กราฟต้นไม้ทอดข้ามสมบูรณ์", "กราฟที่มีค่าน้ำหนักเป็นลบทั้งหมด"],
        "explanation": "Topological Sort เรียงลำดับโหนดตามความสัมพันธ์ก่อนหลัง (Dependencies) ซึ่งจะทำได้ก็ต่อเมื่อกราฟเป็น DAG เท่านั้น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึม 'Floyd-Warshall' ใช้สำหรับคำนวณสิ่งใดในทฤษฎีกราฟ?",
        "correct": "ระยะทางสั้นที่สุดระหว่างทุกคู่โหนด (All-Pairs Shortest Path) ในกราฟ", "distractors": ["การหาเส้นทางเชื่อมต่อที่ยาวที่สุด", "การจัดหมวดหมู่สีของโหนด", "การสร้างผังต้นไม้สองฝั่ง"],
        "explanation": "Floyd-Warshall ใช้ Dynamic Programming คำนวณ Shortest Path ทุกคู่โหนดในกราฟด้วย Time Complexity $O(V^3)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "เทคนิคการเรียงลำดับแบบ 'Merge Sort' ใช้แนวทางการออกแบบอัลกอริทึมแบบใด?",
        "correct": "Divide and Conquer (แบ่งแยกและเอาชนะ)", "distractors": ["Greedy Algorithm (ขั้นตอนละโมบ)", "Backtracking (การย้อนรอย)", "Brute Force (การลองผิดลองถูกทั้งหมด)"],
        "explanation": "Merge Sort แบ่ง Array ครึ่งหนึ่งซ้ำ ๆ จนเหลือขนาด 1 แล้วนำกลับมาผสานเรียงลำดับ (Merge) รวมกันอย่างมีประสิทธิภาพ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูล 'Disjoint Set' (Union-Find) เมื่อใช้เทคนิค Path Compression ร่วมกับ Union by Rank จะมี Time Complexity เฉลี่ยเกือบเป็นเท่าใด?",
        "correct": "$O(\\alpha(n))$ ค่าฟังก์ชันผกผัน Ackermann เกือบเป็นค่าคงที่ $O(1)$", "distractors": ["$O(n^2)$", "$O(n \\log n)$", "$O(n^3)$"],
        "explanation": "Inverse Ackermann function $\\alpha(n)$ เติบโตช้ามาก มีค่าน้อยกว่า 5 สำหรับข้อมูลระดับพันล้านชิ้น ถือว่าเร็วเกือบ $O(1)$"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "อัลกอริทึมการค้นหาข้อความแบบ 'KMP' (Knuth-Morris-Pratt) มีจุดเด่นอย่างไรเหนือ Brute Force?",
        "correct": "ใช้ตาราง LPS (Longest Prefix Suffix) ข้ามการเปรียบเทียบซ้ำซ้อน ทำให้ค้นหาได้เร็วใน $O(n + m)$", "distractors": ["ต้องทำการจัดเรียงตัวอักษรทั้งหมดในข้อความก่อนค้นหา", "ลบคำที่ไม่จำเป็นออกจากข้อความทั้งหมด", "แปลงข้อความเป็นเลขฐานสิบหก"],
        "explanation": "KMP ประมวลผล Pattern ล่วงหน้าสร้างตารางข้ามส่วนที่ตรงกันแล้ว ทำให้ Pointer ฝั่ง Text ไม่ต้องถอยหลังกลับ (No Backtracking)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ความซับซ้อนเชิงพื้นที่ (Space Complexity) ของอัลกอริทึม 'In-Place Sorting' (เช่น Heap Sort) คือเท่าใด?",
        "correct": "$O(1)$ ไม่ต้องใช้หน่วยความจำเพิ่มตามขนาดข้อมูล", "distractors": ["$O(n)$", "$O(n^2)$", "$O(\\log n)$"],
        "explanation": "In-Place Algorithm สลับสับเปลี่ยนสมาชิกภายใน Array เดิมโดยใช้ตัวแปรชั่วคราวคงที่เพียงไม่กี่ตัว ($O(1)$ Auxiliary Space)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในปัญหา 'N-Queens Problem' การวางราชินี N ตัวบนกระดานหมากรุก นิยมใช้วิธีใดในการแก้ปัญหา?",
        "correct": "Backtracking (การย้อนรอยเมื่อพบทางตัน)", "distractors": ["Binary Search", "Breadth-First Search", "Sliding Window"],
        "explanation": "Backtracking วางหมากทีละแถว และย้อนกลับไปลองทางเลือกใหม่ทันทีเมื่อพบว่าจุดปัจจุบันขัดแย้งกับกฎ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "โครงสร้างข้อมูล 'B-Tree' หรือ 'B+ Tree' นิยมนำไปใช้เป็นแกนหลักของระบบใดมากที่สุด?",
        "correct": "ระบบจัดทำดัชนี (Indexing) ของระบบฐานข้อมูลและไฟล์ซิสเต็มบนดิสก์", "distractors": ["โปรแกรมคำนวณคะแนนสอบ", "การ์ดจอสำหรับแสดงภาพ 3D", "ซอฟต์แวร์ควบคุมเมาส์"],
        "explanation": "B/B+ Tree เป็น Multi-way Search Tree ที่ออกแบบมาให้แต่ละโหนดมีขนาดพอดีกับดิสก์บล็อก ช่วยลดจำนวน Disk I/O Operations"
    },

    # -------------------------------------------------------------
    # Category 6: Databases, Software Engineering, AI & Modern Tech (30 questions)
    # -------------------------------------------------------------
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "การทำ Database Normalization ในระดับ '3NF' (Third Normal Form) มีเงื่อนไขหลักอย่างไร?",
        "correct": "ต้องอยู่ใน 2NF และต้องไม่มีการขึ้นต่อกันแบบทรานซิทีฟ (Transitive Dependency)", "distractors": ["ทุกคอลัมน์ต้องเป็นค่าตัวเลขเท่านั้น", "ต้องมีตารางเพียงตารางเดียวในฐานข้อมูล", "ห้ามมี Foreign Key ในตาราง"],
        "explanation": "3NF ขจัด Transitive Dependency คือคอลัมน์ที่ไม่ใช่คีย์หลักต้องไม่ไปขึ้นตรงกับคอลัมน์อื่นที่ไม่ใช่คีย์หลัก"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "คำสั่ง SQL 'HAVING' แตกต่างจากคำสั่ง 'WHERE' อย่างไร?",
        "correct": "HAVING ใช้กรองเงื่อนไขของข้อมูลหลังจากทำ GROUP BY หรือฟังก์ชัน Aggregate แล้ว", "distractors": ["WHERE ใช้ได้เฉพาะกับข้อมูลตัวเลขเท่านั้น", "HAVING ใช้สำหรับลบแถวข้อมูลทิ้งถาวร", "ทั้งสองคำสั่งทำงานเหมือนกันทุกประการ"],
        "explanation": "WHERE ใช้กรอง Record ก่อนนำมารวมกลุ่ม ส่วน HAVING ใช้กรองผลลัพธ์ของกลุ่ม (เช่น HAVING COUNT(*) > 5)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบฐานข้อมูล ระดับการแยกธุรกรรม (Isolation Level) แบบ 'Serializable' มีคุณสมบัติอย่างไร?",
        "correct": "ระดับสูงสุด ป้องกันปัญหา Dirty Read, Non-repeatable Read และ Phantom Read ได้ 100%", "distractors": ["ทำงานเร็วที่สุดแต่ไม่มีความปลอดภัยใด ๆ", "อนุญาตให้อ่านข้อมูลที่ยังไม่ถูก Commit ได้", "ใช้ได้เฉพาะกับฐานข้อมูลแบบ NoSQL"],
        "explanation": "Serializable จำลองการทำงานประหนึ่งว่าแต่ละ Transaction ทำงานเรียงต่อกันทีละตัวอย่างสมบูรณ์ ปลอดภัยที่สุดแต่สูญเสีย Concurrency"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ปัญหา 'Dirty Read' ในระบบฐานข้อมูล Concurrency หมายถึงอะไร?",
        "correct": "ธุรกรรมหนึ่งอ่านข้อมูลที่ถูกแก้ไขโดยอีกธุรกรรมหนึ่งที่ยังไม่ได้ทำการ Commit (และอาจ Rollback ภายหลัง)", "distractors": ["การอ่านข้อมูลจากฮาร์ดดิสก์ที่มีฝุ่นเกาะ", "การพิมพ์คำสั่ง SQL ผิดไวยากรณ์", "การลบตารางฐานข้อมูลโดยไม่ตั้งใจ"],
        "explanation": "Dirty Read เกิดขึ้นเมื่อ Transaction A อ่านข้อมูลที่ Transaction B กำลังแก้อยู่ แล้ว Transaction B เกิด Rollback ยกเลิกข้อมูลนั้น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ทฤษฎีบท 'CAP Theorem' สำหรับระบบกระจายศูนย์ (Distributed Systems) กล่าวว่าระบบสามารถรับประกันคุณสมบัติได้พร้อมกันสูงสุดกี่ข้อ?",
        "correct": "2 ใน 3 ข้อ (จาก Consistency, Availability, Partition Tolerance)", "distractors": ["ครบทั้ง 3 ข้อพร้อมกันเสมอ", "เพียง 1 ข้อเท่านั้น", "ไม่สามารถรับประกันข้อใดได้เลย"],
        "explanation": "เมื่อเกิด Partition ในเครือข่าย ระบบแบบกระจายศูนย์ต้องเลือกระหว่างความสอดคล้องของข้อมูล (C) หรือความพร้อมใช้งาน (A)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หลักการออกแบบ SOLID ตัวอักษร 'S' (Single Responsibility Principle) มีความหมายว่าอย่างไร?",
        "correct": "หนึ่งคลาสหรือหนึ่งโมดูลควรมีหน้าที่รับผิดชอบเพียงเรื่องเดียว และมีเหตุผลเดียวในการเปลี่ยนแปลง", "distractors": ["โปรแกรมควรเขียนโค้ดรวมไว้ในฟังก์ชันเดียว", "คลาสต้องมีขนาดเล็กกว่า 100 ไบต์", "โปรแกรมต้องรันบนเซิร์ฟเวอร์ตัวเดียวเท่านั้น"],
        "explanation": "SRP กำหนดให้แต่ละคลาสมีความรับผิดชอบเฉพาะเจาะจง ไม่ทำงานจับฉ่ายหลายเรื่องปนกัน ช่วยให้แก้โค้ดง่ายโดยไม่กระทบส่วนอื่น"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "หลักการออกแบบ SOLID ตัวอักษร 'O' (Open/Closed Principle) กำหนดแนวทางไว้อย่างไร?",
        "correct": "ซอฟต์แวร์ควรเปิดกว้างสำหรับการต่อขยาย (Open for Extension) แต่ปิดกั้นการแก้ไขโค้ดเดิม (Closed for Modification)", "distractors": ["ต้องเปิดเผยซอร์สโค้ดให้ทุกคนดาวน์โหลดฟรี", "ต้องปิดคอมพิวเตอร์เมื่อเขียนโค้ดเสร็จ", "ห้ามเพิ่มฟีเจอร์ใหม่ลงในโปรแกรม"],
        "explanation": "OCP แนะนำให้ใช้ Polymorphism/Interface ในการเพิ่มความสามารถใหม่ ๆ โดยไม่ต้องไปไล่แก้และทดสอบโค้ดเดิมที่ทำงานถูกต้องอยู่แล้ว"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "รูปแบบการออกแบบ 'Singleton Pattern' รับประกันสิ่งใดในโปรแกรม?",
        "correct": "รับประกันว่าคลาสนั้นจะมีอ็อบเจกต์ (Instance) ถูกสร้างขึ้นเพียง 1 ตัวตลอดการทำงานของโปรแกรม", "distractors": ["รับประกันว่าโปรแกรมจะไม่มีบั๊ก 100%", "รับประกันว่าโปรแกรมจะรันเร็วกว่าเดิม 10 เท่า", "รับประกันว่าโปรแกรมจะเชื่อมต่อกับคลาวด์ได้เสมอ"],
        "explanation": "Singleton จำกัดการสร้าง Instance ให้มีเพียงตัวเดียวในระบบ พร้อมให้ Global Point of Access (เช่น ตัวจัดการ Database Connection Pool)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "รูปแบบการออกแบบ 'Observer Pattern' นิยมนำไปใช้ในสถานการณ์ใด?",
        "correct": "ระบบแจ้งเตือนแบบหนึ่งต่อหลาย (1-to-Many) เมื่อสถานะของอ็อบเจกต์หนึ่งเปลี่ยน อ็อบเจกต์อื่นที่ติดตามจะได้รับการอัปเดตอัตโนมัติ", "distractors": ["การบันทึกภาพวิดีโอจากกล้องวงจรปิด", "การเรียงลำดับตัวเลขในตาราง", "การลบไฟล์ที่ไม่จำเป็นทิ้ง"],
        "explanation": "Observer Pattern เป็นหัวใจของ Event-Driven Systems, UI State Management และ Reactive Programming (Publish-Subscribe)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในการกำหนดเวอร์ชันซอฟต์แวร์ 'Semantic Versioning' (เช่น v2.4.1) เลขตัวแรก (2) มีการปรับเปลี่ยนเมื่อใด?",
        "correct": "เมื่อมีการเปลี่ยนแปลงครั้งใหญ่ที่มีส่วนแก้ไขโค้ดที่ไม่รองรับของเดิม (Breaking Changes)", "distractors": ["เมื่อมีการแก้บั๊กเล็กน้อยประจำวัน", "เมื่อมีการเพิ่มฟีเจอร์ใหม่ที่ยังเข้ากันได้กับของเดิม", "เมื่อเปลี่ยนผู้จัดการโปรเจกต์"],
        "explanation": "SemVer: MAJOR (Breaking changes) . MINOR (New backwards-compatible features) . PATCH (Backwards-compatible bug fixes)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในโมเดล Machine Learning ค่า 'F1-Score' เป็นค่าเฉลี่ยแบบใดระหว่าง Precision และ Recall?",
        "correct": "Harmonic Mean (ค่าเฉลี่ยฮาร์มอนิก)", "distractors": ["Arithmetic Mean (ค่าเฉลี่ยเลขคณิต)", "Geometric Mean (ค่าเฉลี่ยเรขาคณิต)", "Median (มัธยฐาน)"],
        "explanation": "F1-Score คำนวณจาก $2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}}$ ซึ่งเป็น Harmonic Mean เหมาะสำหรับวัดผลเมื่อชุดข้อมูลไม่สมดุล (Imbalanced Data)"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในอัลกอริทึม Gradient Descent หากตั้งค่า 'Learning Rate' (อัตราการเรียนรู้) สูงเกินไปจะเกิดผลเสียอย่างไร?",
        "correct": "โมเดลจะก้าวกระโดดข้ามจุดต่ำสุด (Overshooting) และอาจเกิดการลู่ออก (Diverge) จนไม่สามารถเรียนรู้ได้", "distractors": ["โมเดลจะเรียนรู้ช้าเกินไปจนใช้เวลาเป็นปี", "โมเดลจะจำกัดขนาดของหน่วยความจำแรม", "โมเดลจะลบชุดข้อมูลทิ้งทั้งหมด"],
        "explanation": "Learning Rate ที่ใหญ่เกินไปจะทำให้การอัปเดต Weights แกว่งและกระโดดข้าม Global/Local Minima จน Loss พุ่งสูง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิค 'Dropout' ใน Deep Learning มีไว้เพื่อแก้ปัญหาใดเป็นหลัก?",
        "correct": "ป้องกันปัญหา Overfitting โดยการสุ่มปิดการทำงานของ Neurons บางส่วนระหว่างการฝึก", "distractors": ["เพิ่มความเร็วการเปิดโปรแกรม", "ลดความร้อนของพาวเวอร์ซัพพลาย", "แปลงโมเดลให้กลายเป็นไฟล์เสียง"],
        "explanation": "Dropout บังคับให้โครงข่ายประสาทเรียนรู้ฟีเจอร์ที่แข็งแกร่งและหลากหลาย โดยไม่พึ่งพา Neuron ตัวใดตัวหนึ่งมากเกินไป"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคนิค 'RAG' (Retrieval-Augmented Generation) ช่วยเพิ่มประสิทธิภาพของโมเดล AI (LLM) อย่างไร?",
        "correct": "ดึงข้อมูลอ้างอิงภายนอกที่เกี่ยวข้องมาป้อนเสริมใน Prompt เพื่อให้ตอบคำถามแม่นยำและลดการมั่วข้อมูล (Hallucination)", "distractors": ["เทรนโมเดลใหม่ตั้งแต่ต้นทุกครั้งที่มีผู้ใช้ถาม", "ลบภาษาไทยออกจากโมเดลเพื่อให้ตอบเร็วขึ้น", "เพิ่มจำนวนคอร์ของการ์ดจอ"],
        "explanation": "RAG ค้นหาข้อมูลจาก Knowledge Base/Vector Database แล้วนำมาแนบเป็นบริบทเสริมให้ LLM ตอบได้อย่างแม่นยำและอัปเดต"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ปรากฏการณ์ 'AI Hallucination' ในโมเดลภาษาขนาดใหญ่ (LLMs) หมายถึงสิ่งใด?",
        "correct": "AI สร้างคำตอบที่ดูสมเหตุสมผลและมั่นใจ แต่เป็นข้อมูลเท็จหรือไม่มีอยู่จริง", "distractors": ["AI ปฏิเสธที่จะตอบคำถามของผู้ใช้งาน", "AI ส่งเสียงพูดออกมาจากลำโพงเอง", "AI ทำงานช้าลงเมื่อเวลาผ่านไป"],
        "explanation": "Hallucination คือการที่โมเดล AI ผลิตข้อมูลที่ไม่ตรงกับความเป็นจริงขึ้นมาอย่างมั่นใจเนื่องจากโมเดลคาดเดาตามความน่าจะเป็นของคำ"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ฐานข้อมูลแบบ 'Vector Database' (เช่น Pinecone, Milvus, Chroma) ออกแบบมาเฉพาะเพื่อเก็บและค้นหาสิ่งใด?",
        "correct": "การค้นหาความคล้ายคลึงของเวกเตอร์ (Vector Embeddings) ในงาน AI และ Semantic Search", "distractors": ["เก็บตารางบัญชีเงินเดือนพนักงาน", "เก็บไฟล์เพลง MP3 แบบดั้งเดิม", "เก็บรหัสผ่านผู้ใช้แบบข้อความล้วน"],
        "explanation": "Vector DB ใช้คณิตศาสตร์หาระยะห่าง (Cosine Similarity, Euclidean Distance) ในมิติสูงเพื่อค้นหาความหมายที่ใกล้เคียงกัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบคลาวด์ บริการแบบ 'Serverless' (เช่น AWS Lambda, Google Cloud Functions) มีลักษณะการทำงานอย่างไร?",
        "correct": "รันโค้ดตามเหตุการณ์ (Event-driven) ขยายขนาดอัตโนมัติ และคิดค่าบริการตามเวลาที่โค้ดประมวลผลจริงเท่านั้น", "distractors": ["การรันโปรแกรมโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต", "การใช้เครื่องคอมพิวเตอร์ที่ไม่มีฮาร์ดดิสก์", "การเขียนโปรแกรมโดยไม่ใช้ภาษาโค้ด"],
        "explanation": "Serverless ซ่อนการจัดการเครื่องเซิร์ฟเวอร์ ผู้พัฒนาเพียงอัปโหลดฟังก์ชัน ระบบจะ Scale อัตโนมัติจาก 0 ถึงล้านคำขอและคิดเงินตามระยะเวลาที่รัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ซอฟต์แวร์ 'Kubernetes' (K8s) มีหน้าที่หลักคืออะไรในระบบ Infrastructure?",
        "correct": "ระบบจัดการ บริหาร ควบคุม และปรับขนาดอัตโนมัติสำหรับ Containerized Applications (Container Orchestration)", "distractors": ["โปรแกรมแอนติไวรัสสำหรับเครื่องแมค", "โปรแกรมจำลองเกมเพลย์สเตชัน", "ภาษาเขียนโปรแกรมสำหรับสร้างเว็บ"],
        "explanation": "Kubernetes จัดการ Deployment, Scaling, Self-healing และ Load Balancing ของ Docker Containers บน Cluster ขนาดใหญ่"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ระบบจัดการข้อความ 'Message Broker' (เช่น Apache Kafka, RabbitMQ) ช่วยพัฒนาระบบอย่างไร?",
        "correct": "ช่วยตัดการเชื่อมโยงโดยตรง (Decoupling) และส่งต่อข้อมูลระหว่างเซอร์วิสแบบ Asynchronous", "distractors": ["ช่วยแปลภาษาหน้าเว็บอัตโนมัติ", "ช่วยเพิ่มความสว่างของหน้าจอคอมพิวเตอร์", "ช่วยติดตั้งระบบปฏิบัติการลงในไดรฟ์"],
        "explanation": "Message Broker รับประกันการส่งต่อข้อมูลแบบ Asynchronous ช่วยให้ระบบ Microservices ไม่ต้องรอผลลัพธ์แบบ Blocking"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในวงการฐานข้อมูล กลไก 'Sharding' มีประโยชน์อย่างไร?",
        "correct": "การแบ่งแยกข้อมูลขนาดใหญ่ออกเป็นส่วนย่อย ๆ ตามแนวนอนกระจายลงหลายเซิร์ฟเวอร์ (Horizontal Partitioning)", "distractors": ["การบีบอัดฐานข้อมูลให้เป็นไฟล์ Zip", "การลบข้อมูลที่เก่าเกิน 1 ปีทิ้งทั้งหมด", "การแปลงข้อมูลข้อความเป็นตัวเลข"],
        "explanation": "Database Sharding ช่วยขยายขนาดระบบ (Scale-out) โดยแบ่งแถวข้อมูลไปเก็บตาม Shard ต่าง ๆ บนเซิร์ฟเวอร์หลายเครื่อง"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในกระบวนการประมวลผลธุรกรรม '2-Phase Commit' (2PC) ถูกนำมาใช้แก้ปัญหาใด?",
        "correct": "การันตีความเป็นเอกภาพ (Atomicity) ของการทำ Transaction ที่กระจายอยู่บนฐานข้อมูลหลายแห่ง (Distributed Transactions)", "distractors": ["การกดปุ่มบันทึกงานสองครั้งเพื่อความแน่ใจ", "การสำรองข้อมูลลงแผ่นซีดี 2 แผ่น", "การเพิ่มความเร็วการค้นหาในตาราง 2 เท่า"],
        "explanation": "2PC มี 2 ขั้นตอนคือ Prepare Phase (ถามความพร้อมทุกโหนด) และ Commit/Abort Phase เพื่อรับประกันว่าทุกฐานข้อมูล Commit พร้อมกัน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "คำสั่งใน Git ข้อใดใช้สำหรับสลับกิ่งทำงาน (Branch) ไปยังกิ่งอื่น?",
        "correct": "git switch (หรือ git checkout)", "distractors": ["git push", "git init", "git status"],
        "explanation": "git switch (คำสั่งใหม่ที่ชัดเจน) หรือ git checkout ใช้สำหรับสลับไปยัง Branch ที่ต้องการทำงาน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "คำสั่ง 'git rebase' แตกต่างจาก 'git merge' ในประวัติการทำงานของ Git อย่างไร?",
        "correct": "Rebase ย้ายฐานประวัติคอมมิตไปต่อท้ายกิ่งเป้าหมาย ทำให้เส้นประวัติการทำงานเป็นเส้นตรงสวยงาม", "distractors": ["Rebase ลบโค้ดทั้งหมดในโปรเจกต์ทิ้ง", "Merge ไม่สามารถรวมโค้ดสองกิ่งเข้าด้วยกันได้", "Rebase ใช้สำหรับอัปโหลดโค้ดขึ้น GitHub เท่านั้น"],
        "explanation": "Rebase เขียนประวัติใหม่ให้ต่อกันเป็นเส้นตรงเดี่ยว (Linear History) ส่วน Merge จะคงประวัติและสร้าง Merge Commit ขึ้นมาเชื่อม"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ระบบ 'GraphQL' มีข้อได้เปรียบเหนือ 'REST API' ในเรื่องใด?",
        "correct": "Client สามารถระบุโครงสร้างและเลือกฟิลด์ข้อมูลที่ต้องการได้อย่างเจาะจง แก้ปัญหา Over-fetching / Under-fetching", "distractors": ["GraphQL ไม่จำเป็นต้องใช้การเชื่อมต่อเครือข่าย", "GraphQL แปลงข้อมูลเป็นรูปภาพได้โดยตรง", "GraphQL ใช้ได้เฉพาะกับภาษา JavaScript เท่านั้น"],
        "explanation": "GraphQL ช่วยให้ฝั่งหน้าบ้านขอเฉพาะข้อมูลฟิลด์ที่ต้องการใน Query เดียว ไม่ต้องยิงหลาย Endpoint เหมือน REST"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในภาษา SQL คำสั่ง 'TRUNCATE TABLE' แตกต่างจาก 'DELETE FROM' อย่างไร?",
        "correct": "TRUNCATE ล้างข้อมูลทั้งหมดในตารางและรีเซ็ตค่า Auto Increment เร็วกว่าโดยไม่บันทึก Log รายแถว", "distractors": ["DELETE ลบตารางและโครงสร้างตารางทิ้งไปจากฐานข้อมูล", "TRUNCATE สามารถเลือกใส่เงื่อนไข WHERE ได้", "ทั้งสองคำสั่งทำงานช้าเร็วเท่ากัน"],
        "explanation": "TRUNCATE เป็นคำสั่ง DDL ที่ Drop และ Re-create ตารางอย่างรวดเร็ว ส่วน DELETE เป็น DML ที่ไล่ลบทีละแถวและรองรับ WHERE"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในกระบวนการ Machine Learning 'Confusion Matrix' ให้ข้อมูลสถิติสิ่งใด?",
        "correct": "ตารางสรุปผลการทำนาย: True Positive (TP), True Negative (TN), False Positive (FP), False Negative (FN)", "distractors": ["ตารางแสดงความเร็วในการคำนวณของซีพียู", "ตารางเปรียบเทียบราคาของการ์ดจอ", "ตารางแสดงขนาดของไฟล์โมเดล"],
        "explanation": "Confusion Matrix ใช้ประเมินประสิทธิภาพของ Classification Model นำไปคำนวณต่อเป็น Accuracy, Precision, Recall และ Specificity"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "เทคโนโลยี 'Vectorization' หรือ 'SIMD' (Single Instruction, Multiple Data) ใน CPU ช่วยเพิ่มความเร็วการประมวลผลข้อมูลอย่างไร?",
        "correct": "สั่งคำสั่งเดียวแต่ประมวลผลข้อมูลหลายชุดในเวกเตอร์รีจิสเตอร์พร้อมกันใน 1 รอบสัญญาณ", "distractors": ["การใส่ซิมการ์ดโทรศัพท์ลงในคอมพิวเตอร์", "การเพิ่มพัดลมระบายความร้อนอีก 1 ตัว", "การลบคำสั่งที่ซ้ำซ้อนทิ้งอัตโนมัติ"],
        "explanation": "SIMD (เช่น SSE, AVX, NEON) ประมวลผลชุดตัวเลขหลายตัวพร้อมกันใน Register ขนาดใหญ่ เหมาะกับงานกราฟิก เสียง และ AI"
    },
    {
        "category_key": "cat_cs", "difficulty": "ปานกลาง",
        "text": "ในวงการพัฒนาเว็บ 'Single Page Application' (SPA เช่น React, Vue) มีการทำงานอย่างไร?",
        "correct": "โหลดไฟล์ HTML หลักเพียงครั้งเดียว แล้วใช้ JavaScript จัดการดึงข้อมูลและเรนเดอร์เปลี่ยนหน้าโดยไม่ต้องรีเฟรชทั้งจอ", "distractors": ["เว็บไซต์ที่มีเนื้อหาเพียงหน้าเดียวและไม่มีปุ่มกดใด ๆ", "เว็บไซต์ที่เปิดได้เฉพาะบนหน้าจอขนาด 15 นิ้ว", "เว็บไซต์ที่ห้ามเชื่อมต่อกับฐานข้อมูล"],
        "explanation": "SPA โหลด Shell หน้าเว็บครั้งแรก แล้วสลับเนื้อหาผ่าน Client-side Routing ให้ความรู้สึกลื่นไหลเสมือนแอปบนเดสก์ท็อป"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในระบบฐานข้อมูล 'Write-Ahead Logging' (WAL) มีไว้เพื่อวัตถุประสงค์ใด?",
        "correct": "บันทึกการเปลี่ยนแปลงลงใน Log File บนดิสก์ก่อนนำไปเขียนลงตารางจริง เพื่อรับประกันความปลอดภัยหากไฟดับหรือระบบล่ม", "distractors": ["เขียนโค้ดล่วงหน้าก่อนที่ผู้ใช้จะสมัครสมาชิก", "ส่งอีเมลเตือนผู้ดูแลระบบทุกชั่วโมง", "ปิดการใช้งานฐานข้อมูลเมื่อไม่มีคนเข้าชม"],
        "explanation": "WAL เป็นหัวใจของ Durability ใน ACID รับประกันว่าถ้าเครื่องดับ ระบบจะสามารถ Replay Log กู้ข้อมูลกลับมาได้ครบถ้วน"
    },
    {
        "category_key": "cat_cs", "difficulty": "ยาก",
        "text": "ในสถาปัตยกรรมแบบ Microservices ปัญหา 'Distributed Tracing' นิยมแก้ไขด้วยเครื่องมือประเภทใด?",
        "correct": "การแนบ Trace ID และ Span ID ไปกับทุกคำขอเพื่อติดตามเส้นทางข้ามเซอร์วิส (เช่น OpenTelemetry, Jaeger)", "distractors": ["การรวมทุกเซอร์วิสกลับมาเป็นก้อน Monolith เดียวกัน", "การปิดระบบเน็ตเวิร์กแล้วใช้สายโทรศัพท์แทน", "การบันทึกภาพหน้าจอทุกวินาที"],
        "explanation": "Distributed Tracing ส่ง Trace Context ผ่าน HTTP/gRPC Headers ช่วยให้เห็นขวดความหน่วงและจุดเกิด Error ในระบบที่ซับซ้อน"
    },
]

print(f"Total new questions defined: {len(new_200_questions)}")
