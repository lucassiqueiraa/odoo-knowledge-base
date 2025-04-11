from odoo import models, fields, api
from datetime import datetime, timedelta


class HrAttendanceAutoCheckout(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def _cron_auto_checkout(self):
        """Tarefa agendada para verificar check-ins sem check-outs e registrar automaticamente o checkout no fim do expediente."""

        # Buscar registros de check-in sem check-out
        checkins = self.search([('check_out', '=', False)])

        for checkin in checkins:
            employee = checkin.employee_id
            calendar = employee.resource_calendar_id  # Horário de trabalho do funcionário

            if not calendar:
                continue  # Se não houver calendário, não pode calcular a jornada de trabalho

            check_in_time = checkin.check_in
            check_in_date = check_in_time.date()

            # Obter os horários de expediente do funcionário para o dia do check-in
            work_hours = calendar.attendance_ids.filtered(lambda a: a.dayofweek == str(check_in_date.weekday()))

            if not work_hours:
                continue  # Se não há horário de trabalho definido para esse dia, pula

            # Pegar o horário FINAL do expediente (último horário do dia)
            last_work_hour = max(work_hours, key=lambda wh: wh.hour_to)

            work_start = datetime.combine(check_in_date, datetime.min.time()) + timedelta(
                hours=last_work_hour.hour_from)
            work_end = datetime.combine(check_in_date, datetime.min.time()) + timedelta(hours=last_work_hour.hour_to)

            # Verifica se o check-in foi dentro do horário de trabalho e que o check-out ainda não foi marcado
            if work_start <= check_in_time <= work_end and not checkin.check_out:
                checkin.write({'check_out': work_end})
