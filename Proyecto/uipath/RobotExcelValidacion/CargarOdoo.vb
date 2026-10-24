' Segunda etapa de Main.xaml. VALIDAR es predeterminado; VERIFICAR conecta sin escribir.
Dim modoRpa As String = If(Environment.GetEnvironmentVariable("RPA_MODO"), "VALIDAR").Trim().ToUpperInvariant()
If modoRpa <> "CARGAR" AndAlso modoRpa <> "VERIFICAR" Then
    System.Diagnostics.Trace.WriteLine("RPA: modo VALIDAR; no se hicieron llamadas autenticadas ni escrituras en Odoo.")
Else
    Dim rutaLote As String = Environment.GetEnvironmentVariable("RPA_LOTE_ACTUAL")
    If String.IsNullOrWhiteSpace(rutaLote) OrElse Not System.IO.File.Exists(rutaLote) Then Throw New System.IO.FileNotFoundException("No se encontró el lote validado de esta ejecución.")
    Dim credencial As String = Environment.GetEnvironmentVariable("RPA_CREDENCIAL")
    If String.IsNullOrWhiteSpace(credencial) Then credencial = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "QuetzalMartRPA", "credencial.dat")
    If Not System.IO.File.Exists(credencial) Then Throw New System.IO.FileNotFoundException("Falta la credencial local del robot. Ejecuta GuardarCredencial.ps1.")
    Dim lineas As String() = System.IO.File.ReadAllLines(credencial)
    If lineas.Length <> 2 OrElse String.IsNullOrWhiteSpace(lineas(0)) Then Throw New InvalidOperationException("El archivo de credencial no tiene el formato esperado.")
    Dim usuario As String = lineas(0).Trim()
    Dim protegida As Byte() = Convert.FromBase64String(lineas(1))
    Dim clara As Byte() = System.Security.Cryptography.ProtectedData.Unprotect(protegida, Nothing, System.Security.Cryptography.DataProtectionScope.CurrentUser)
    Dim claveApi As String = System.Text.Encoding.UTF8.GetString(clara)
    System.Array.Clear(clara, 0, clara.Length)
    System.Array.Clear(protegida, 0, protegida.Length)
    Dim servidor As String = Environment.GetEnvironmentVariable("RPA_ODOO_URL")
    If String.IsNullOrWhiteSpace(servidor) Then servidor = "https://136.116.120.10"
    servidor = servidor.TrimEnd("/"c)
    Dim pruebaLocal As Boolean = String.Equals(Environment.GetEnvironmentVariable("RPA_PRUEBA_LOCAL"), "1", StringComparison.Ordinal)
    If Not servidor.StartsWith("https://", StringComparison.OrdinalIgnoreCase) AndAlso Not (pruebaLocal AndAlso servidor.StartsWith("http://127.0.0.1:", StringComparison.OrdinalIgnoreCase)) Then Throw New InvalidOperationException("RPA_ODOO_URL debe usar HTTPS.")
    Dim baseDatos As String = Environment.GetEnvironmentVariable("RPA_ODOO_DB")
    If String.IsNullOrWhiteSpace(baseDatos) Then baseDatos = "quetzalmart_db"
    System.Net.ServicePointManager.SecurityProtocol = CType(3072, System.Net.SecurityProtocolType)
    Dim rutaJson As String = System.IO.Path.Combine(System.Runtime.InteropServices.RuntimeEnvironment.GetRuntimeDirectory(), "System.Web.Extensions.dll")
    Dim tipoJson As Type = System.Reflection.Assembly.LoadFrom(rutaJson).GetType("System.Web.Script.Serialization.JavaScriptSerializer", True)
    Dim serializador As Object = System.Activator.CreateInstance(tipoJson)
    tipoJson.GetProperty("MaxJsonLength").SetValue(serializador, Integer.MaxValue, Nothing)
    Dim aJson As Func(Of Object, String) = Function(valor As Object) CStr(tipoJson.GetMethod("Serialize", New Type() {GetType(Object)}).Invoke(serializador, New Object() {valor}))
    Dim deJson As Func(Of String, Object) = Function(valor As String) tipoJson.GetMethod("DeserializeObject", New Type() {GetType(String)}).Invoke(serializador, New Object() {valor})
    Dim registros As Object() = DirectCast(deJson(System.IO.File.ReadAllText(rutaLote, System.Text.Encoding.UTF8)), Object())
    Dim vacio As New System.Collections.Generic.Dictionary(Of String, Object)()
    Dim numeroLlamada As Integer = 0
    Dim rpc As Func(Of String, String, Object(), Object) = Function(servicio As String, metodo As String, argumentos As Object()) As Object
        numeroLlamada += 1
        Dim parametros As New System.Collections.Generic.Dictionary(Of String, Object) From {{"service", servicio}, {"method", metodo}, {"args", argumentos}}
        Dim mensaje As New System.Collections.Generic.Dictionary(Of String, Object) From {{"jsonrpc", "2.0"}, {"method", "call"}, {"params", parametros}, {"id", numeroLlamada}}
        Dim bytes As Byte() = System.Text.Encoding.UTF8.GetBytes(aJson(mensaje))
        Dim solicitud As System.Net.HttpWebRequest = DirectCast(System.Net.WebRequest.Create(servidor & "/jsonrpc"), System.Net.HttpWebRequest)
        solicitud.Method = "POST"
        solicitud.ContentType = "application/json"
        solicitud.Accept = "application/json"
        solicitud.Timeout = 60000
        solicitud.ReadWriteTimeout = 60000
        solicitud.ContentLength = bytes.Length
        Using entrada As System.IO.Stream = solicitud.GetRequestStream()
            entrada.Write(bytes, 0, bytes.Length)
        End Using
        System.Array.Clear(bytes, 0, bytes.Length)
        Dim respuestaTexto As String
        Using respuestaHttp As System.Net.HttpWebResponse = DirectCast(solicitud.GetResponse(), System.Net.HttpWebResponse)
            Using lector As New System.IO.StreamReader(respuestaHttp.GetResponseStream(), System.Text.Encoding.UTF8)
                respuestaTexto = lector.ReadToEnd()
            End Using
        End Using
        Dim respuesta As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(deJson(respuestaTexto), System.Collections.Generic.Dictionary(Of String, Object))
        If respuesta.ContainsKey("error") AndAlso respuesta("error") IsNot Nothing Then
            Dim fallo As System.Collections.Generic.Dictionary(Of String, Object) = TryCast(respuesta("error"), System.Collections.Generic.Dictionary(Of String, Object))
            Dim detalle As String = If(fallo Is Nothing OrElse Not fallo.ContainsKey("message"), "Error no especificado", Convert.ToString(fallo("message")))
            Throw New InvalidOperationException("Odoo rechazó la operación: " & detalle)
        End If
        If Not respuesta.ContainsKey("result") Then Throw New InvalidOperationException("Odoo respondió sin result.")
        Return respuesta("result")
    End Function
    Dim uid As Integer = Convert.ToInt32(rpc("common", "authenticate", New Object() {baseDatos, usuario, claveApi, New System.Collections.Generic.Dictionary(Of String, Object)()}))
    If uid <= 0 Then Throw New InvalidOperationException("Odoo rechazó la autenticación del usuario de integración.")
    Dim llamar As Func(Of String, String, Object(), System.Collections.Generic.Dictionary(Of String, Object), Object) = Function(modelo As String, metodo As String, argumentos As Object(), opciones As System.Collections.Generic.Dictionary(Of String, Object)) As Object
        Return rpc("object", "execute_kw", New Object() {baseDatos, uid, claveApi, modelo, metodo, argumentos, opciones})
    End Function
    Dim buscar As Func(Of String, Object(), String(), Integer, Object()) = Function(modelo As String, dominio As Object(), campos As String(), limite As Integer) As Object()
        Dim opciones As New System.Collections.Generic.Dictionary(Of String, Object) From {{"fields", campos}, {"limit", limite}}
        Return DirectCast(llamar(modelo, "search_read", New Object() {dominio}, opciones), Object())
    End Function
    Dim porCampo As Func(Of String, String, String, Object()) = Function(modelo As String, campo As String, valor As String) As Object()
        Return buscar(modelo, New Object() {New Object() {campo, "=", valor}}, New String() {"id"}, 2)
    End Function
    Dim idUnico As Func(Of String, String, String, Integer) = Function(modelo As String, campo As String, valor As String) As Integer
        Dim hallados As Object() = porCampo(modelo, campo, valor)
        If hallados.Length > 1 Then Throw New InvalidOperationException("Más de un registro de " & modelo & " coincide con " & campo & "=" & valor)
        If hallados.Length = 0 Then Return 0
        Return Convert.ToInt32(DirectCast(hallados(0), System.Collections.Generic.Dictionary(Of String, Object))("id"))
    End Function
    Dim campoTexto As Func(Of System.Collections.Generic.Dictionary(Of String, Object), String, String) = Function(fila As System.Collections.Generic.Dictionary(Of String, Object), nombre As String) As String
        Return If(fila.ContainsKey(nombre), Convert.ToString(fila(nombre)).Trim(), "")
    End Function
    Dim numero As Func(Of String, Double) = Function(valor As String) As Double
        Dim resultado As Double
        If Double.TryParse(valor, System.Globalization.NumberStyles.Number, System.Globalization.CultureInfo.InvariantCulture, resultado) Then Return resultado
        If Double.TryParse(valor, System.Globalization.NumberStyles.Number, System.Globalization.CultureInfo.CurrentCulture, resultado) Then Return resultado
        Throw New FormatException("Número inválido: " & valor)
    End Function
    Dim distinto As Func(Of Object, Object, Boolean) = Function(actual As Object, deseado As Object) As Boolean
        If deseado Is Nothing Then Return actual IsNot Nothing
        If TypeOf deseado Is Boolean Then Return Convert.ToBoolean(actual) <> CBool(deseado)
        If TypeOf deseado Is Double Then Return Math.Abs(Convert.ToDouble(actual) - CDbl(deseado)) > 0.00001R
        If TypeOf deseado Is Integer Then
            Dim par As Object() = TryCast(actual, Object())
            Dim actualId As Integer = If(par Is Nothing, If(actual Is Nothing OrElse TypeOf actual Is Boolean, 0, Convert.ToInt32(actual)), Convert.ToInt32(par(0)))
            Return actualId <> CInt(deseado)
        End If
        If TypeOf deseado Is Object() Then
            Dim comandos As Object() = DirectCast(deseado, Object())
            Dim comando As Object() = DirectCast(comandos(0), Object())
            Dim deseados As Integer() = DirectCast(comando(2), Integer())
            Dim actuales As Object() = If(TryCast(actual, Object()), New Object() {})
            Return Not deseados.OrderBy(Function(x) x).SequenceEqual(actuales.Select(Function(x) Convert.ToInt32(x)).OrderBy(Function(x) x))
        End If
        Return Not String.Equals(Convert.ToString(actual), Convert.ToString(deseado), StringComparison.Ordinal)
    End Function

    Dim metadatos As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(llamar("product.template", "fields_get", New Object() {}, vacio), System.Collections.Generic.Dictionary(Of String, Object))
    For Each requerido As String In New String() {"x_rpa_external_id", "x_rpa_product_values", "type", "is_published", "product_variant_id"}
        If Not metadatos.ContainsKey(requerido) Then Throw New InvalidOperationException("Falta el campo " & requerido & " en product.template. Revisa la preparación de Odoo.")
    Next
    If modoRpa = "VERIFICAR" Then
        buscar("res.partner", New Object() {}, New String() {"id"}, 1)
        buscar("product.template", New Object() {}, New String() {"id"}, 1)
        buscar("stock.quant", New Object() {}, New String() {"id"}, 1)
        Dim permisos As New System.Collections.Generic.Dictionary(Of String, Object)()
        For Each modelo As String In New String() {"res.partner", "res.partner.category", "product.template", "product.category", "stock.quant"}
            Dim opcionesPermiso As New System.Collections.Generic.Dictionary(Of String, Object) From {{"raise_exception", False}}
            Dim crear As Boolean = Convert.ToBoolean(llamar(modelo, "check_access_rights", New Object() {"create"}, opcionesPermiso))
            Dim editar As Boolean = Convert.ToBoolean(llamar(modelo, "check_access_rights", New Object() {"write"}, opcionesPermiso))
            permisos(modelo) = New System.Collections.Generic.Dictionary(Of String, Object) From {{"crear", crear}, {"editar", editar}}
        Next
        Dim comprobacion As New System.Collections.Generic.Dictionary(Of String, Object) From {{"url", servidor}, {"base", baseDatos}, {"usuario", usuario}, {"uid", uid}, {"contactos", "lectura_ok"}, {"productos", "lectura_ok"}, {"inventario", "lectura_ok"}, {"permisos", permisos}, {"escrituras", 0}}
        Dim rutaConexion As String = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(rutaLote), "conexion_" & DateTime.Now.ToString("yyyyMMdd_HHmmss") & ".json")
        System.IO.File.WriteAllText(rutaConexion, aJson(comprobacion), New System.Text.UTF8Encoding(False))
        System.Diagnostics.Trace.WriteLine("RPA conexión verificada sin escrituras: " & rutaConexion)
        If permisos.Values.Any(Function(p) Not Convert.ToBoolean(DirectCast(p, System.Collections.Generic.Dictionary(Of String, Object))("crear")) OrElse Not Convert.ToBoolean(DirectCast(p, System.Collections.Generic.Dictionary(Of String, Object))("editar"))) Then Throw New InvalidOperationException("La cuenta se autentica, pero faltan permisos de creación o edición. Revisa el reporte de conexión.")
    Else
    Dim rutaCarga As String = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(rutaLote), "carga_" & System.IO.Path.GetFileNameWithoutExtension(rutaLote).Substring(5) & ".csv")
    Dim comilla As String = ChrW(34).ToString()
    Dim csv As Func(Of String, String) = Function(valor As String) comilla & If(valor, "").Replace(comilla, comilla & comilla) & comilla
    Dim creados As Integer = 0
    Dim actualizados As Integer = 0
    Dim omitidos As Integer = 0
    Dim errores As Integer = 0
    Dim ordenados As System.Collections.Generic.IEnumerable(Of Object) = registros.OrderBy(Function(x)
        Dim fila As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(x, System.Collections.Generic.Dictionary(Of String, Object))
        If campoTexto(fila, "_tipo") = "productos" Then Return 2
        Return If({"company", "empresa"}.Contains(campoTexto(fila, "company type").ToLowerInvariant()), 0, 1)
    End Function)

    Using reporte As New System.IO.StreamWriter(rutaCarga, False, New System.Text.UTF8Encoding(True))
        reporte.WriteLine("Archivo,Hoja,Fila,Tipo,Clave,Accion,OdooID,Motivo,URL")
        For Each objeto As Object In ordenados
            Dim fila As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(objeto, System.Collections.Generic.Dictionary(Of String, Object))
            Dim tipo As String = campoTexto(fila, "_tipo")
            Dim clave As String = campoTexto(fila, "_clave")
            Dim accion As String = "ERROR"
            Dim motivo As String = ""
            Dim id As Integer = 0
            Dim urlProducto As String = ""
            Try
                Dim valores As New System.Collections.Generic.Dictionary(Of String, Object)()
                valores("name") = campoTexto(fila, "name")
                Dim coincidencias As New System.Collections.Generic.HashSet(Of Integer)()
                If tipo = "clientes" Then
                    For Each par As System.Collections.Generic.KeyValuePair(Of String, String) In New System.Collections.Generic.Dictionary(Of String, String) From {{"reference", "ref"}, {"tax id", "vat"}, {"email", "email"}}
                        Dim valor As String = campoTexto(fila, par.Key)
                        If valor <> "" Then
                            Dim encontrado As Integer = idUnico("res.partner", par.Value, valor)
                            If encontrado > 0 Then coincidencias.Add(encontrado)
                        End If
                    Next
                    If coincidencias.Count > 1 Then Throw New InvalidOperationException("Las claves del cliente apuntan a contactos diferentes.")
                    If coincidencias.Count = 1 Then id = coincidencias.First()
                    Dim empresa As String = campoTexto(fila, "company type").ToLowerInvariant()
                    If empresa <> "" Then valores("company_type") = If(empresa = "company" OrElse empresa = "empresa", "company", "person")
                    For Each par As System.Collections.Generic.KeyValuePair(Of String, String) In New System.Collections.Generic.Dictionary(Of String, String) From {{"reference", "ref"}, {"tax id", "vat"}, {"email", "email"}, {"phone", "phone"}, {"street", "street"}, {"street2", "street2"}, {"city", "city"}, {"zip", "zip"}, {"website", "website"}, {"notes", "comment"}}
                        Dim valor As String = campoTexto(fila, par.Key)
                        If valor <> "" Then valores(par.Value) = valor
                    Next
                    Dim pais As String = campoTexto(fila, "country")
                    Dim paisId As Integer = 0
                    If pais <> "" Then
                        paisId = idUnico("res.country", "name", pais)
                        If paisId = 0 Then paisId = idUnico("res.country", "code", pais.ToUpperInvariant())
                        If paisId = 0 Then Throw New InvalidOperationException("País no encontrado: " & pais)
                        valores("country_id") = paisId
                    End If
                    Dim estado As String = campoTexto(fila, "state")
                    If estado <> "" Then
                        Dim dominio As Object() = If(paisId > 0, New Object() {New Object() {"name", "=", estado}, New Object() {"country_id", "=", paisId}}, New Object() {New Object() {"name", "=", estado}})
                        Dim estados As Object() = buscar("res.country.state", dominio, New String() {"id"}, 2)
                        If estados.Length <> 1 Then Throw New InvalidOperationException("Estado inexistente o ambiguo: " & estado)
                        valores("state_id") = Convert.ToInt32(DirectCast(estados(0), System.Collections.Generic.Dictionary(Of String, Object))("id"))
                    End If
                    Dim relacionada As String = campoTexto(fila, "related company")
                    If relacionada <> "" Then
                        Dim empresas As Object() = buscar("res.partner", New Object() {New Object() {"name", "=", relacionada}, New Object() {"company_type", "=", "company"}}, New String() {"id"}, 2)
                        If empresas.Length > 1 Then Throw New InvalidOperationException("Empresa relacionada ambigua: " & relacionada)
                        If empresas.Length = 0 Then
                            valores("parent_id") = Convert.ToInt32(llamar("res.partner", "create", New Object() {New System.Collections.Generic.Dictionary(Of String, Object) From {{"name", relacionada}, {"company_type", "company"}, {"comment", "Empresa relacionada creada por la carga RPA"}}}, vacio))
                            motivo = "Se creó la empresa relacionada"
                        Else
                            valores("parent_id") = Convert.ToInt32(DirectCast(empresas(0), System.Collections.Generic.Dictionary(Of String, Object))("id"))
                        End If
                    End If
                    Dim etiquetas As String = campoTexto(fila, "tags")
                    If etiquetas <> "" Then
                        Dim ids As New System.Collections.Generic.List(Of Integer)()
                        For Each etiqueta As String In etiquetas.Split(New Char() {";"c, ","c}, StringSplitOptions.RemoveEmptyEntries)
                            Dim nombre As String = etiqueta.Trim()
                            Dim etiquetaId As Integer = idUnico("res.partner.category", "name", nombre)
                            If etiquetaId = 0 Then etiquetaId = Convert.ToInt32(llamar("res.partner.category", "create", New Object() {New System.Collections.Generic.Dictionary(Of String, Object) From {{"name", nombre}}}, vacio))
                            ids.Add(etiquetaId)
                        Next
                        valores("category_id") = New Object() {New Object() {6, 0, ids.Distinct().ToArray()}}
                    End If
                ElseIf tipo = "productos" Then
                    For Each par As System.Collections.Generic.KeyValuePair(Of String, String) In New System.Collections.Generic.Dictionary(Of String, String) From {{"id externo", "x_rpa_external_id"}, {"internal reference", "default_code"}, {"barcode", "barcode"}}
                        Dim valor As String = campoTexto(fila, par.Key)
                        If valor <> "" Then
                            Dim encontrado As Integer = idUnico("product.template", par.Value, valor)
                            If encontrado > 0 Then coincidencias.Add(encontrado)
                        End If
                    Next
                    If coincidencias.Count > 1 Then Throw New InvalidOperationException("Las claves del producto apuntan a productos diferentes.")
                    If coincidencias.Count = 1 Then id = coincidencias.First()
                    For Each par As System.Collections.Generic.KeyValuePair(Of String, String) In New System.Collections.Generic.Dictionary(Of String, String) From {{"id externo", "x_rpa_external_id"}, {"internal reference", "default_code"}, {"barcode", "barcode"}, {"sales description", "description_sale"}, {"product values", "x_rpa_product_values"}}
                        Dim valor As String = campoTexto(fila, par.Key)
                        If valor <> "" Then valores(par.Value) = valor
                    Next
                    Dim grupoProducto As String = campoTexto(fila, "product values")
                    If grupoProducto <> "" AndAlso Not grupoProducto.Contains(":") Then
                        Dim categoriaId As Integer = idUnico("product.category", "name", grupoProducto)
                        If categoriaId = 0 Then categoriaId = Convert.ToInt32(llamar("product.category", "create", New Object() {New System.Collections.Generic.Dictionary(Of String, Object) From {{"name", grupoProducto}}}, vacio))
                        valores("categ_id") = categoriaId
                    End If
                    For Each par As System.Collections.Generic.KeyValuePair(Of String, String) In New System.Collections.Generic.Dictionary(Of String, String) From {{"sales price", "list_price"}, {"cost", "standard_price"}, {"weight", "weight"}}
                        Dim valor As String = campoTexto(fila, par.Key)
                        If valor <> "" Then valores(par.Value) = numero(valor)
                    Next
                    Dim clase As String = campoTexto(fila, "product type").ToLowerInvariant()
                    If clase <> "" Then
                        Dim codigo As String = If({"goods", "bien", "bienes", "producto"}.Contains(clase), "consu", If({"service", "servicio"}.Contains(clase), "service", "combo"))
                        valores("type") = codigo
                        If metadatos.ContainsKey("is_storable") Then valores("is_storable") = (codigo = "consu")
                    End If
                    Dim publicacion As String = campoTexto(fila, "esta publicado").ToLowerInvariant()
                    If publicacion <> "" Then valores("is_published") = ({"sí", "si", "true", "1"}.Contains(publicacion))
                    valores("sale_ok") = True
                Else
                    Throw New InvalidOperationException("Tipo de hoja no admitido: " & tipo)
                End If

                Dim modelo As String = If(tipo = "clientes", "res.partner", "product.template")
                If id = 0 Then
                    id = Convert.ToInt32(llamar(modelo, "create", New Object() {valores}, vacio))
                    accion = "CREADO"
                    creados += 1
                Else
                    Dim campos As String() = valores.Keys.ToArray()
                    Dim actuales As Object() = buscar(modelo, New Object() {New Object() {"id", "=", id}}, campos, 1)
                    If actuales.Length <> 1 Then Throw New InvalidOperationException("El registro encontrado desapareció antes de actualizarlo.")
                    Dim actual As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(actuales(0), System.Collections.Generic.Dictionary(Of String, Object))
                    Dim cambio As Boolean = valores.Any(Function(p) Not actual.ContainsKey(p.Key) OrElse distinto(actual(p.Key), p.Value))
                    If cambio Then
                        llamar(modelo, "write", New Object() {New Integer() {id}, valores}, vacio)
                        accion = "ACTUALIZADO"
                        actualizados += 1
                    Else
                        accion = "OMITIDO"
                        omitidos += 1
                    End If
                End If
                Dim verificados As Object() = buscar(modelo, New Object() {New Object() {"id", "=", id}}, New String() {"id", "name"}, 1)
                If verificados.Length <> 1 OrElse Not String.Equals(Convert.ToString(DirectCast(verificados(0), System.Collections.Generic.Dictionary(Of String, Object))("name")), campoTexto(fila, "name"), StringComparison.Ordinal) Then Throw New InvalidOperationException("No se pudo verificar el registro después de escribir.")

                If tipo = "productos" Then
                    Dim detalle As Object() = buscar("product.template", New Object() {New Object() {"id", "=", id}}, New String() {"product_variant_id", "type", "is_published", "website_url"}, 1)
                    Dim producto As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(detalle(0), System.Collections.Generic.Dictionary(Of String, Object))
                    If producto.ContainsKey("website_url") AndAlso TypeOf producto("website_url") Is String Then urlProducto = servidor & Convert.ToString(producto("website_url"))
                    Dim cantidad As String = campoTexto(fila, "cantidad a la mano")
                    If cantidad <> "" Then
                        If Convert.ToString(producto("type")) <> "consu" Then
                            If numero(cantidad) <> 0R Then Throw New InvalidOperationException("Cantidad positiva en un producto que no es Goods.")
                        Else
                            Dim variante As Object() = TryCast(producto("product_variant_id"), Object())
                            If variante Is Nothing Then Throw New InvalidOperationException("El producto no tiene variante principal para inventario.")
                            Dim varianteId As Integer = Convert.ToInt32(variante(0))
                            Dim ubicaciones As Object() = buscar("stock.warehouse", New Object() {New Object() {"code", "=", "WH"}}, New String() {"lot_stock_id"}, 2)
                            If ubicaciones.Length <> 1 Then Throw New InvalidOperationException("No se encontró un único almacén WH.")
                            Dim almacen As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(ubicaciones(0), System.Collections.Generic.Dictionary(Of String, Object))
                            Dim ubicacionId As Integer = Convert.ToInt32(DirectCast(almacen("lot_stock_id"), Object())(0))
                            Dim quants As Object() = buscar("stock.quant", New Object() {New Object() {"product_id", "=", varianteId}, New Object() {"location_id", "=", ubicacionId}}, New String() {"id", "quantity", "lot_id", "owner_id", "package_id"}, 2)
                            If quants.Length > 1 Then Throw New InvalidOperationException("Hay varios quants en WH/Stock; se requiere revisar lote o propietario.")
                            Dim deseada As Double = numero(cantidad)
                            Dim quantId As Integer = 0
                            If quants.Length = 1 Then
                                Dim quant As System.Collections.Generic.Dictionary(Of String, Object) = DirectCast(quants(0), System.Collections.Generic.Dictionary(Of String, Object))
                                If TypeOf quant("lot_id") Is Object() OrElse TypeOf quant("owner_id") Is Object() OrElse TypeOf quant("package_id") Is Object() Then Throw New InvalidOperationException("El inventario usa lote, propietario o paquete; requiere revisión manual.")
                                quantId = Convert.ToInt32(quant("id"))
                                If Math.Abs(Convert.ToDouble(quant("quantity")) - deseada) > 0.00001R Then
                                    Dim contextoInventario As New System.Collections.Generic.Dictionary(Of String, Object) From {{"context", New System.Collections.Generic.Dictionary(Of String, Object) From {{"inventory_mode", True}}}}
                                    llamar("stock.quant", "write", New Object() {New Integer() {quantId}, New System.Collections.Generic.Dictionary(Of String, Object) From {{"inventory_quantity", deseada}}}, contextoInventario)
                                    llamar("stock.quant", "action_apply_inventory", New Object() {New Integer() {quantId}}, contextoInventario)
                                End If
                            ElseIf deseada > 0R Then
                                Dim contextoInventario As New System.Collections.Generic.Dictionary(Of String, Object) From {{"context", New System.Collections.Generic.Dictionary(Of String, Object) From {{"inventory_mode", True}}}}
                                quantId = Convert.ToInt32(llamar("stock.quant", "create", New Object() {New System.Collections.Generic.Dictionary(Of String, Object) From {{"product_id", varianteId}, {"location_id", ubicacionId}, {"inventory_quantity", deseada}}}, contextoInventario))
                                llamar("stock.quant", "action_apply_inventory", New Object() {New Integer() {quantId}}, contextoInventario)
                            End If
                            If quantId > 0 Then
                                Dim finales As Object() = buscar("stock.quant", New Object() {New Object() {"id", "=", quantId}}, New String() {"quantity"}, 1)
                                If finales.Length <> 1 OrElse Math.Abs(Convert.ToDouble(DirectCast(finales(0), System.Collections.Generic.Dictionary(Of String, Object))("quantity")) - deseada) > 0.00001R Then Throw New InvalidOperationException("El inventario no coincide con la cantidad solicitada.")
                            End If
                        End If
                    End If
                    If campoTexto(fila, "esta publicado") <> "" Then
                        Dim deseado As Boolean = {"sí", "si", "true", "1"}.Contains(campoTexto(fila, "esta publicado").ToLowerInvariant())
                        If Convert.ToBoolean(producto("is_published")) <> deseado Then Throw New InvalidOperationException("La publicación del producto no coincide con el Excel.")
                    End If
                End If
            Catch ex As Exception
                errores += 1
                motivo = ex.Message
                accion = "ERROR"
            End Try
            reporte.WriteLine(String.Join(",", {csv(campoTexto(fila, "_archivo")), csv(campoTexto(fila, "_hoja")), csv(campoTexto(fila, "_fila")), csv(tipo), csv(clave), csv(accion), csv(If(id = 0, "", id.ToString())), csv(motivo), csv(urlProducto)}))
            reporte.Flush()
        Next
    End Using
    System.Diagnostics.Trace.WriteLine("RPA carga: creados=" & creados & ", actualizados=" & actualizados & ", omitidos=" & omitidos & ", errores=" & errores & "; reporte=" & rutaCarga)
    End If
End If
