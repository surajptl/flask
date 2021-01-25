from flask import Flask, request, jsonify, json
from werkzeug.exceptions import HTTPException
from enum import Enum

server = Flask(__name__)

#Need to move in other files/folder
class Constants(Enum):
    PremiumPaymentGateway = "PremiumPaymentGateway"
    ExpensivePaymentGateway = "ExpensivePaymentGateway"
    CheapPaymentGateway = "CheapPaymentGateway"
    StringType = ['CreditCardNumber', 'CardHolder', 'ExpirationDate', 'SecurityCode']
    DoubleType = 'Amount'

#Need to move in other files/folder
class CustomRequired(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
    
#to handle exceptions
# @server.errorhandler(CustomRequired)
# def handle_error(e):
#     code = 500
#     if isinstance(e, HTTPException):
#         code = e.code
#     return jsonify(error=str(e)), code


#Need to move in other files/folder
#to validate required inputs
class Validator:
    @classmethod
    def validate_kwargs(cls, kwargs, required_keys):
        validation_flag, key = cls.isset_kwargs(kwargs, required_keys)
        if not validation_flag:
            raise CustomRequired('Key {} has invalid value.'.format(key))

    @classmethod
    def isset_kwargs(cls, kwargs, required_keys):
        for key in required_keys:
            if key not in kwargs or kwargs[key] is None or kwargs[key] == '':
                return False, key

        return True, None

#payment methods
class Payments:
    __cheapTry = 1
    __PremiumTry = 3

    def __init__(self, CreditCardNumber, CardHolder, ExpirationDate, Amount, SecurityCode=None):
        self.CreditCardNumber = CreditCardNumber
        self.CardHolder = CardHolder
        self.ExpirationDate = ExpirationDate
        self.Amount = Amount
        self.SecurityCode = SecurityCode
        self.checkExpensiveService = True
        self.cheap_payment_try = 0
        self.premium_payment_try = 0
        self.CheckAmountAndProceedWithPayment()


    def PremiumPaymentGateway(self):
        if self.premium_payment_try < self.__PremiumTry:
            try:
                print("proceed with premium payment")
            except:
                self.premium_payment_try += 1
                self.PremiumPaymentGateway()


    def ExpensivePaymentGateway(self):
        print("proceed with expensive payment")
    
    def CheapPaymentGateway(self, expensive_payment=False):
        if expensive_payment:
            self.cheap_payment_try += 1
        #proceed with payment
        print("proceed with cheap payment")


    def CheckAmountAndProceedWithPayment(self):
        amount  = self.Amount
        if amount < 20:
            self.CheapPaymentGateway()
        elif amount >= 21 and amount < 500:
            if self.checkExpensiveService:
                self.ExpensivePaymentGateway()
            else:
                if self.cheap_payment_try < self.__cheapTry:
                    self.CheapPaymentGateway(expensive_payment=True)
                else:
                    pass #we can't proceed with cheap payment now
        elif amount >= 500:
            self.ExpensivePaymentGateway()


@server.route('/proceed-payment/', methods=['POST'])
def proceed_payment():
    def typecast(requested_data):
        for key in Constants.StringType.value:
            if requested_data.get(key) and isinstance(requested_data[key],str):
                #Need to log 
                pass
            else:
                raise CustomRequired('Key {} has invalid type.'.format(key))
        if requested_data.get(Constants.DoubleType.value) and isinstance(requested_data[Constants.DoubleType.value], float):
            try:
                requested_data[Constants.DoubleType.name] = float(requested_data[Constants.DoubleType.value])
            except:
                raise CustomRequired('Key {} has invalid type.'.format(Constants.DoubleType.value))
            #Need to log
        return requested_data
    
    #get typecast data
    requested_data = typecast(request.get_json())

    #validate required key
    Validator.validate_kwargs(requested_data, ['CreditCardNumber', 'CardHolder', 'ExpirationDate', 'Amount'])

    #Business Logic
    payment = Payments(CreditCardNumber=requested_data.get("CreditCardNumber"), CardHolder=requested_data.get("CardHolder")\
        , ExpirationDate=requested_data.get("ExpirationDate"), Amount=requested_data.get("Amount"), SecurityCode=requested_data.get("SecurityCode"))
    # payment.CheckAmountAndProceedWithPayment()

    response = server.response_class(
        response=json.dumps({'message': "Payment Proceed Successfully"}),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    server.run(debug=True)
