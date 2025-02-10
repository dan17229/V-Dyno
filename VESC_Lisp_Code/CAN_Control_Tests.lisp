(define can-cnt 0) ; Counter for received CAN-frames

(define proc-sid
    (lambda (id data)
        (print (list "Received ID:" id "Data:" data)) ; Print the ID and data
        (print (bits-dec-int data 0 6))
        ; Set the motor RPM based on the data received
        (let ((rpm (bits-dec-int data 0 6))) ; Assuming the RPM value is in the first 32 bits of data
            (set-rpm rpm) ; Set the motor RPM
            (print (list "Setting RPM to:" rpm)) ; Print the RPM value being set
        )
    )
)

(define event-handler
    (lambda ()
        (progn
            (recv ((event-can-sid (? id) . (? data))
                                 (proc-sid id data))
                                (_ nil)) ; Ignore other events
            (event-handler) ; Call self again to make this a loop
        )
    )
)

; Spawn the event handler thread and pass the ID it returns to C
(event-register-handler (spawn event-handler))

; Enable the CAN event for standard ID (SID) frames
(event-enable 'event-can-sid)

(loopwhile t {
        (set-btn-leds btn-now 1 4 1)
        (sleep 1.5)
        (set-btn-leds btn-now 0 0 0)
        
        (setq btn-now (+ btn-now 1))
        (if (= btn-now 6) (def btn-now 7)) ; Index 6 is missing, so skip it
        (if (> btn-now 7) (def btn-now 1))
})
