
from flask_restful import Resource
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from webargs.flaskparser import use_kwargs
from webargs import fields
from models.ResponseCodes import ResponseCodes
from models.ResponseCodes import ResponseDescriptions
from api.models.models import db_session, CurrentBalance


def serialize_current_balance(current_balance: CurrentBalance):
    return {"Id": current_balance.id,
            "Date": current_balance.date.strftime('%Y-%m-%d'),
            "CurrBal1": current_balance.currbal1,
            "CurrBal10": current_balance.currbal10,
            "CurrBal100": current_balance.currbal100,
            "CurrBal1000": current_balance.currbal1000,
            "CurrBal10000": current_balance.currbal10000,
            "CurrBal50000": current_balance.currbal50000,
            "CurrBalGT50000": current_balance.currbalgt50000
            }


class CurrentBalanceByDateEndpoint(Resource):
    get_args = {"Date": fields.Date()
                }
    insert_args = {
        "Date": fields.Date(),
        "CurrBal1": fields.Integer(),
        "CurrBal10": fields.Integer(),
        "CurrBal100": fields.Integer(),
        "CurrBal1000": fields.Integer(),
        "CurrBal10000": fields.Integer(),
        "CurrBal50000": fields.Integer(),
        "CurrBalGT50000": fields.Integer()
    }

    @use_kwargs(insert_args)
    def post(self, Date,
             CurrBal1=None,
             CurrBal10=None,
             CurrBal100=None,
             CurrBal1000=None,
             CurrBal10000=None,
             CurrBal50000=None,
             CurrBalGT50000=None):

        current_balance = CurrentBalance(date=Date,
                                              currbal1=CurrBal1,
                                              currbal10=CurrBal10,
                                              currbal100=CurrBal100,
                                              currbal1000=CurrBal1000,
                                              currbal10000=CurrBal10000,
                                              currbal50000=CurrBal50000,
                                              currbalgt50000=CurrBalGT50000
                                              )
        db_session.add(current_balance)
        try:
            db_session.commit()
            response = {"ResponseCode": ResponseCodes.Success.value,
                        "ResponseDesc": ResponseCodes.Success.name,
                        "CurrentBalance": serialize_current_balance(current_balance)}
        except SQLAlchemyError as e:
            print(str(e))
            db_session.rollback()
            response = {"ResponseCode": ResponseCodes.InternalError.value,
                        "ResponseDesc": ResponseCodes.InternalError.name,
                        "ErrorMessage": ResponseDescriptions.ErrorFromDataBase.value}

        return response

    @use_kwargs(get_args)
    def get(self, Date=None):

        error = self.validateCurrentBalanceInput(Date)
        if error is not None:
            return {"ResponseCode": ResponseCodes.InvalidRequestParameter.value,
                    "ResponseDesc": ResponseCodes.InvalidRequestParameter.name,
                    "ErrorMessage": error.value}

        current_balance = db_session.query(CurrentBalance).filter(
            and_(CurrentBalance.date == Date)).one_or_none()

        if current_balance is None:
            response = {"ResponseCode": ResponseCodes.NoDataFound.value,
                        "ResponseDesc": ResponseCodes.NoDataFound.name,
                        "ErrorMessage": ResponseDescriptions.NoDataFound.value}
        else:
            response = {"ResponseCode": ResponseCodes.Success.value,
                        "ResponseDesc": ResponseCodes.Success.name,
                        "CurrentBalance": serialize_current_balance(current_balance)}

        return response

    def validateCurrentBalanceInput(self, date):
        error = None

        if date is None:
            error = ResponseDescriptions.DateInputMissing
        else:
            try:
                date.strftime('%Y-%m-%d')
            except ValueError:
                error = ResponseDescriptions.DateInputMissing
        return error
