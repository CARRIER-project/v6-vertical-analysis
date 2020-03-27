FROM datasharing_base:v2.0

COPY generate_receiver_keys.py generate_receiver_keys.py
COPY generate_sender_keys.py generate_sender_keys.py

COPY overview_request.py overview_request.py
COPY overview_subfunctions.py overview_subfunctions.py

COPY sign_model.py sign_model.py

COPY check_format.py check_format.py
COPY encrypt_data.py encrypt_data.py
COPY salt_hashing.py salt_hashing.py

COPY analysis_subfunctions.py analysis_subfunctions.py
COPY analysis_main.py analysis_main.py
COPY matching.py matching.py
COPY verify_decrypt.py verify_decrypt.py

COPY run.py run.py

CMD ["python3", "run.py"]
