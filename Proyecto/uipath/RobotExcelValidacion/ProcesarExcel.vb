' Código de la actividad Invoke Code de Main.xaml (VB.NET, Windows - Legacy).
' Primera etapa: prepara un lote local. No se conecta a Odoo.
Dim raiz As String = Environment.GetEnvironmentVariable("RPA_ENTRADA")
If String.IsNullOrWhiteSpace(raiz) Then
    raiz = System.IO.Path.GetFullPath(System.IO.Path.Combine(Environment.CurrentDirectory, "..", "..", "datos_prueba", "rpa"))
End If
If Not System.IO.Directory.Exists(raiz) Then
    Throw New System.IO.DirectoryNotFoundException("No existe la carpeta de entrada: " & raiz)
End If

Dim carpetaReporte As String = System.IO.Path.Combine(Environment.CurrentDirectory, "Reportes")
System.IO.Directory.CreateDirectory(carpetaReporte)
Dim sello As String = DateTime.Now.ToString("yyyyMMdd_HHmmss")
Dim rutaReporte As String = System.IO.Path.Combine(carpetaReporte, "validacion_" & sello & ".csv")
Dim normalizar As Func(Of String, String) = Function(valor As String)
    Dim descompuesto As String = If(valor, "").Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    Dim texto As New System.Text.StringBuilder()
    For Each caracter As Char In descompuesto
        If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(caracter) <> System.Globalization.UnicodeCategory.NonSpacingMark Then
            texto.Append(caracter)
        End If
    Next
    Return System.Text.RegularExpressions.Regex.Replace(texto.ToString().Normalize(System.Text.NormalizationForm.FormC), "\s+", " ")
End Function
Dim comilla As String = ChrW(34).ToString()
Dim csv As Func(Of String, String) = Function(valor As String) comilla & If(valor, "").Replace(comilla, comilla & comilla) & comilla
Dim vistos As New System.Collections.Generic.Dictionary(Of String, String)(StringComparer.OrdinalIgnoreCase)
Dim registros As New System.Collections.Generic.List(Of System.Collections.Generic.Dictionary(Of String, Object))()
Dim libros As Integer = 0
Dim hojas As Integer = 0
Dim validos As Integer = 0
Dim rechazados As Integer = 0
Dim omitidosDuplicados As Integer = 0
Dim posicion5 As Integer = 0
Dim posicionDistinta As Integer = 0
Dim erroresArchivo As Integer = 0
Dim excel As Microsoft.Office.Interop.Excel.Application = Nothing

Using reporte As New System.IO.StreamWriter(rutaReporte, False, New System.Text.UTF8Encoding(True))
    reporte.WriteLine("Archivo,Hoja,Posicion,Fila,Tipo,Clave,Estado,Motivo")
    Try
        excel = New Microsoft.Office.Interop.Excel.Application()
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.AskToUpdateLinks = False
        excel.AutomationSecurity = Microsoft.Office.Core.MsoAutomationSecurity.msoAutomationSecurityForceDisable

        For Each ruta As String In System.IO.Directory.EnumerateFiles(raiz, "*.*", System.IO.SearchOption.AllDirectories).OrderBy(Function(x) x, StringComparer.OrdinalIgnoreCase)
            Dim extension As String = System.IO.Path.GetExtension(ruta).ToLowerInvariant()
            If Not ({".xlsx", ".xls", ".xlsm"}.Contains(extension)) OrElse System.IO.Path.GetFileName(ruta).StartsWith("~$") Then
                Continue For
            End If
            libros += 1
            Dim objetivosLibro As Integer = 0
            Dim libro As Microsoft.Office.Interop.Excel.Workbook = Nothing
            Try
                libro = excel.Workbooks.Open(ruta, 0, True)
                For indice As Integer = 1 To libro.Worksheets.Count
                    Dim hoja As Microsoft.Office.Interop.Excel.Worksheet = Nothing
                    Dim rango As Microsoft.Office.Interop.Excel.Range = Nothing
                    Try
                        hoja = DirectCast(libro.Worksheets.Item(indice), Microsoft.Office.Interop.Excel.Worksheet)
                        Dim tipo As String = normalizar(hoja.Name)
                        If tipo <> "clientes" AndAlso tipo <> "productos" Then
                            Continue For
                        End If
                        hojas += 1
                        objetivosLibro += 1
                        If indice = 5 Then
                            posicion5 += 1
                        Else
                            posicionDistinta += 1
                            reporte.WriteLine(String.Join(",", {csv(ruta), csv(hoja.Name), csv(indice.ToString()), csv(""), csv(tipo), csv(""), csv("AVISO"), csv("Hoja objetivo fuera de la quinta posición")}))
                        End If
                        rango = hoja.UsedRange
                        Dim datos As Object = rango.Value2
                        Dim matriz As System.Array = TryCast(datos, System.Array)
                        Dim filas As Integer = rango.Rows.Count
                        Dim columnas As Integer = rango.Columns.Count
                        Dim primeraFila As Integer = rango.Row
                        Dim primeraColumna As Integer = rango.Column
                        Dim celda As Func(Of Integer, Integer, String) = Function(f As Integer, c As Integer)
                            Dim valor As Object = Nothing
                            If matriz IsNot Nothing Then
                                valor = matriz.GetValue(f, c)
                            ElseIf f = 1 AndAlso c = 1 Then
                                valor = datos
                            End If
                            Return If(valor Is Nothing, "", Convert.ToString(valor, System.Globalization.CultureInfo.InvariantCulture).Trim())
                        End Function

                        Dim encabezado As Integer = 0
                        Dim candidatos As Integer = 0
                        Dim indices As New System.Collections.Generic.Dictionary(Of String, Integer)(StringComparer.OrdinalIgnoreCase)
                        Dim noVacias As Integer = 0
                        For f As Integer = 1 To filas
                            Dim mapa As New System.Collections.Generic.Dictionary(Of String, Integer)(StringComparer.OrdinalIgnoreCase)
                            Dim repetido As Boolean = False
                            For c As Integer = 1 To columnas
                                Dim nombre As String = normalizar(celda(f, c))
                                If nombre <> "" Then
                                    If mapa.ContainsKey(nombre) Then
                                        repetido = True
                                    Else
                                        mapa.Add(nombre, c)
                                    End If
                                End If
                            Next
                            If mapa.Count = 0 Then
                                Continue For
                            End If
                            noVacias += 1
                            If mapa.ContainsKey("name") AndAlso (If(tipo = "clientes", mapa.ContainsKey("reference") OrElse mapa.ContainsKey("tax id") OrElse mapa.ContainsKey("email"), mapa.ContainsKey("id externo") OrElse mapa.ContainsKey("internal reference") OrElse mapa.ContainsKey("barcode"))) Then
                                candidatos += 1
                                If Not repetido Then
                                    encabezado = f
                                    indices = mapa
                                Else
                                    encabezado = 0
                                End If
                            End If
                            If noVacias >= 10 Then
                                Exit For
                            End If
                        Next

                        If candidatos <> 1 OrElse encabezado = 0 Then
                            Dim motivo As String = If(candidatos = 0, "Encabezado obligatorio ausente", If(candidatos > 1, "Encabezado ambiguo", "Encabezado repetido"))
                            reporte.WriteLine(String.Join(",", {csv(ruta), csv(hoja.Name), csv(indice.ToString()), csv(""), csv(tipo), csv(""), csv("RECHAZADO"), csv(motivo)}))
                            rechazados += 1
                            Continue For
                        End If

                        For f As Integer = encabezado + 1 To filas
                            Dim vacia As Boolean = True
                            For c As Integer = 1 To columnas
                                If celda(f, c) <> "" Then
                                    vacia = False
                                    Exit For
                                End If
                            Next
                            If vacia Then
                                Continue For
                            End If
                            Dim filaActual As Integer = f
                            Dim obtener As Func(Of String, String) = Function(nombre As String)
                                Dim col As Integer = 0
                                Return If(indices.TryGetValue(nombre, col), celda(filaActual, col), "")
                            End Function
                            Dim clave As String = ""
                            Dim campoClave As String = ""
                            Dim motivos As New System.Collections.Generic.List(Of String)()
                            If obtener("name") = "" Then motivos.Add("Name vacío")
                            For Each nombre As String In If(tipo = "clientes", New String() {"reference", "tax id", "email"}, New String() {"id externo", "internal reference", "barcode"})
                                If obtener(nombre) <> "" Then
                                    campoClave = nombre
                                    clave = obtener(nombre)
                                    Exit For
                                End If
                            Next
                            If clave = "" Then motivos.Add("Sin identificador confiable")

                            If tipo = "clientes" Then
                                Dim correo As String = obtener("email")
                                If correo <> "" AndAlso Not System.Text.RegularExpressions.Regex.IsMatch(correo, "^[^\s@]+@[^\s@]+\.[^\s@]+$") Then
                                    motivos.Add("Email inválido")
                                End If
                                Dim tipoEmpresa As String = normalizar(obtener("company type"))
                                If tipoEmpresa <> "" AndAlso Not ({"company", "person", "empresa", "persona", "individual", "persona individual"}.Contains(tipoEmpresa)) Then
                                    motivos.Add("Company Type desconocido")
                                End If
                            Else
                                Dim tipoProducto As String = normalizar(obtener("product type"))
                                If tipoProducto <> "" AndAlso Not ({"goods", "service", "combo", "bien", "bienes", "servicio", "producto"}.Contains(tipoProducto)) Then
                                    motivos.Add("Product Type desconocido")
                                End If
                                For Each nombre As String In New String() {"sales price", "cost", "weight", "cantidad a la mano"}
                                    Dim texto As String = obtener(nombre)
                                    If texto <> "" Then
                                        Dim numero As Decimal
                                        If Not Decimal.TryParse(texto, System.Globalization.NumberStyles.Number, System.Globalization.CultureInfo.InvariantCulture, numero) AndAlso Not Decimal.TryParse(texto, System.Globalization.NumberStyles.Number, System.Globalization.CultureInfo.CurrentCulture, numero) Then
                                            motivos.Add(nombre & " no es numérico")
                                        ElseIf numero < 0D Then
                                            motivos.Add(nombre & " negativo")
                                        End If
                                    End If
                                Next
                                Dim publicado As String = normalizar(obtener("esta publicado"))
                                If publicado <> "" AndAlso Not ({"si", "no", "true", "false", "1", "0"}.Contains(publicado)) Then
                                    motivos.Add("Está publicado inválido")
                                End If
                            End If
                            Dim clavesFila As New System.Collections.Generic.List(Of String)()
                            Dim duplicadoIdentico As Boolean = False
                            If motivos.Count = 0 Then
                                For Each nombre As String In If(tipo = "clientes", New String() {"reference", "tax id", "email"}, New String() {"id externo", "internal reference", "barcode"})
                                    If obtener(nombre) <> "" Then clavesFila.Add(tipo & "|" & nombre & "|" & obtener(nombre).Trim().ToLowerInvariant())
                                Next
                                Dim firma As String = String.Join(ChrW(30).ToString(), indices.Keys.OrderBy(Function(k) k, StringComparer.Ordinal).Select(Function(k) k & "=" & obtener(k)))
                                Dim repetidas As String() = clavesFila.Where(Function(k) vistos.ContainsKey(k)).ToArray()
                                If repetidas.Length > 0 Then
                                    If repetidas.Length = clavesFila.Count AndAlso repetidas.All(Function(k) String.Equals(vistos(k), firma, StringComparison.Ordinal)) Then
                                        duplicadoIdentico = True
                                    Else
                                        motivos.Add("Clave repetida con datos distintos")
                                    End If
                                Else
                                    For Each claveFila As String In clavesFila
                                        vistos.Add(claveFila, firma)
                                    Next
                                End If
                            End If
                            Dim estado As String = If(duplicadoIdentico, "OMITIDO", If(motivos.Count = 0, "VALIDADO", "RECHAZADO"))
                            If duplicadoIdentico Then
                                omitidosDuplicados += 1
                            ElseIf motivos.Count = 0 Then
                                validos += 1
                            Else
                                rechazados += 1
                            End If
                            Dim motivoFila As String = If(duplicadoIdentico, "Fila idéntica ya vista", String.Join("; ", motivos))
                            reporte.WriteLine(String.Join(",", {csv(ruta), csv(hoja.Name), csv(indice.ToString()), csv((primeraFila + f - 1).ToString()), csv(tipo), csv(clave), csv(estado), csv(motivoFila)}))
                            If estado = "VALIDADO" Then
                                Dim registro As New System.Collections.Generic.Dictionary(Of String, Object)(StringComparer.OrdinalIgnoreCase)
                                registro("_archivo") = ruta
                                registro("_hoja") = hoja.Name
                                registro("_posicion") = indice
                                registro("_fila") = primeraFila + f - 1
                                registro("_tipo") = tipo
                                registro("_clave") = clave
                                For Each columna As System.Collections.Generic.KeyValuePair(Of String, Integer) In indices
                                    registro(columna.Key) = celda(filaActual, columna.Value)
                                Next
                                registros.Add(registro)
                            End If
                        Next
                    Catch ex As Exception
                        rechazados += 1
                        reporte.WriteLine(String.Join(",", {csv(ruta), csv(If(hoja Is Nothing, "", hoja.Name)), csv(indice.ToString()), csv(""), csv("hoja"), csv(""), csv("ERROR"), csv(ex.Message)}))
                    Finally
                        If rango IsNot Nothing Then System.Runtime.InteropServices.Marshal.FinalReleaseComObject(rango)
                        If hoja IsNot Nothing Then System.Runtime.InteropServices.Marshal.FinalReleaseComObject(hoja)
                    End Try
                Next
                If objetivosLibro = 0 Then
                    reporte.WriteLine(String.Join(",", {csv(ruta), csv(""), csv(""), csv(""), csv("libro"), csv(""), csv("OMITIDO"), csv("Sin hojas clientes o productos")}))
                End If
            Catch ex As Exception
                rechazados += 1
                erroresArchivo += 1
                reporte.WriteLine(String.Join(",", {csv(ruta), csv(""), csv(""), csv(""), csv("libro"), csv(""), csv("ERROR"), csv(ex.Message)}))
            Finally
                If libro IsNot Nothing Then
                    libro.Close(False)
                    System.Runtime.InteropServices.Marshal.FinalReleaseComObject(libro)
                End If
            End Try
        Next
    Finally
        If excel IsNot Nothing Then
            excel.Quit()
            System.Runtime.InteropServices.Marshal.FinalReleaseComObject(excel)
        End If
    End Try
End Using
Dim rutaLote As String = System.IO.Path.Combine(carpetaReporte, "lote_" & sello & ".json")
Dim etapaJson As String = "cargar ensamblado"
Try
    Dim rutaJson As String = System.IO.Path.Combine(System.Runtime.InteropServices.RuntimeEnvironment.GetRuntimeDirectory(), "System.Web.Extensions.dll")
    Dim tipoJson As Type = System.Reflection.Assembly.LoadFrom(rutaJson).GetType("System.Web.Script.Serialization.JavaScriptSerializer", True)
    etapaJson = "crear serializador"
    Dim serializador As Object = System.Activator.CreateInstance(tipoJson)
    tipoJson.GetProperty("MaxJsonLength").SetValue(serializador, Integer.MaxValue, Nothing)
    Dim aJson As Func(Of Object, String) = Function(valor As Object) CStr(tipoJson.GetMethod("Serialize", New Type() {GetType(Object)}).Invoke(serializador, New Object() {valor}))
    etapaJson = "escribir lote"
    System.IO.File.WriteAllText(rutaLote, aJson(registros), New System.Text.UTF8Encoding(False))
    Dim resumen As New System.Collections.Generic.Dictionary(Of String, Object) From {{"carpeta_entrada", raiz}, {"libros_revisados", libros}, {"hojas_objetivo", hojas}, {"posicion_5", posicion5}, {"posicion_distinta", posicionDistinta}, {"filas_validas", validos}, {"omitidos_duplicados", omitidosDuplicados}, {"rechazados", rechazados}, {"errores_archivo", erroresArchivo}, {"reporte_csv", rutaReporte}, {"lote_json", rutaLote}}
    etapaJson = "escribir resumen"
    System.IO.File.WriteAllText(System.IO.Path.Combine(carpetaReporte, "resumen_" & sello & ".json"), aJson(resumen), New System.Text.UTF8Encoding(False))
Catch ex As Exception
    System.IO.File.WriteAllText(System.IO.Path.Combine(carpetaReporte, "diagnostico_" & sello & ".txt"), etapaJson & Environment.NewLine & ex.ToString(), New System.Text.UTF8Encoding(False))
    Throw
End Try
Environment.SetEnvironmentVariable("RPA_LOTE_ACTUAL", rutaLote, EnvironmentVariableTarget.Process)
Environment.SetEnvironmentVariable("RPA_REPORTE_ACTUAL", rutaReporte, EnvironmentVariableTarget.Process)
System.Diagnostics.Trace.WriteLine("RPA validación: libros=" & libros & ", hojas=" & hojas & ", válidos=" & validos & ", rechazados=" & rechazados & "; reporte=" & rutaReporte)
