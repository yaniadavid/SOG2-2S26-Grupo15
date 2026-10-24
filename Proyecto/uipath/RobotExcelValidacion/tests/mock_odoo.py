"""Servidor JSON-RPC local para probar el robot sin escribir en Odoo real."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


DATA = {"res.partner": {}, "product.template": {}, "stock.quant": {}, "res.partner.category": {}, "product.category": {}}
NEXT = {"res.partner": 100, "product.template": 200, "stock.quant": 300, "res.partner.category": 400, "product.category": 500}


def related(value):
    if isinstance(value, list) and value and isinstance(value[0], list):
        return value
    return value


def match(record, domain):
    for field, operator, value in domain:
        actual = record.get(field)
        if field == "id":
            actual = record["id"]
        elif isinstance(actual, list) and actual and not isinstance(actual[0], list):
            actual = actual[0]
        if operator != "=" or actual != value:
            return False
    return True


def search_read(model, args, kwargs):
    domain = args[0]
    if model == "res.country":
        rows = [{"id": 1, "name": "Guatemala", "code": "GT"}, {"id": 2, "name": "El Salvador", "code": "SV"}]
    elif model == "res.country.state":
        rows = [{"id": 1, "name": "Guatemala", "country_id": 1}, {"id": 2, "name": "La Libertad", "country_id": 2}, {"id": 3, "name": "San Salvador", "country_id": 2}]
    elif model == "res.partner.category":
        rows = [{"id": i, "name": name} for i, name in enumerate(("cliente frecuente", "mayorista", "minorista", "proveedor aliado", "nuevo", "corporativo", "vip", "Prueba"), 1)] + list(DATA[model].values())
    elif model == "stock.warehouse":
        rows = [{"id": 1, "code": "WH", "lot_stock_id": [8, "WH/Stock"]}]
    else:
        rows = list(DATA[model].values())
    fields = kwargs.get("fields", [])
    limit = kwargs.get("limit", 100)
    result = []
    for row in rows:
        if match(row, domain):
            item = {key: row.get(key, False) for key in fields}
            item["id"] = row["id"]
            result.append(item)
    return result[:limit]


def write_values(record, values):
    for field, value in values.items():
        if field == "category_id" and value:
            record[field] = value[0][2]
        elif field == "inventory_quantity":
            record[field] = value
        elif field in ("country_id", "state_id", "parent_id", "categ_id"):
            record[field] = [value, str(value)]
        else:
            record[field] = value


def execute(model, method, args, kwargs):
    if method == "fields_get":
        return {name: {"type": "char"} for name in (
            "x_rpa_external_id", "x_rpa_product_values", "type", "is_published",
            "product_variant_id", "is_storable", "website_url",
        )}
    if method == "search_read":
        return search_read(model, args, kwargs)
    if method == "create":
        NEXT[model] += 1
        record = {"id": NEXT[model]}
        write_values(record, args[0])
        if model == "product.template":
            record["product_variant_id"] = [record["id"] + 1000, record["name"]]
            record["website_url"] = f"/shop/mock-{record['id']}"
            record.setdefault("is_published", False)
        if model == "stock.quant":
            record.setdefault("quantity", 0)
        DATA[model][record["id"]] = record
        return record["id"]
    if method == "write":
        for record_id in args[0]:
            write_values(DATA[model][record_id], args[1])
        return True
    if method == "action_apply_inventory":
        for record_id in args[0]:
            record = DATA[model][record_id]
            record["quantity"] = record["inventory_quantity"]
        return True
    raise ValueError(f"Método no implementado: {model}.{method}")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(size))
            params = payload["params"]
            if params["service"] == "common":
                result = 42 if params["args"][2] == "fake-key" else False
            else:
                _, uid, key, model, method, args, kwargs = params["args"]
                if uid != 42 or key != "fake-key":
                    raise ValueError("Credencial de prueba inválida")
                result = execute(model, method, args, kwargs)
            answer = {"jsonrpc": "2.0", "id": payload["id"], "result": result}
        except Exception as exc:
            answer = {"jsonrpc": "2.0", "id": payload.get("id"), "error": {"message": str(exc)}}
        encoded = json.dumps(answer).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 18069), Handler).serve_forever()
