"""Inserta ProcesarExcel.vb en Main.xaml para UiPath Studio 2021.10."""

from pathlib import Path
from xml.sax.saxutils import quoteattr


root = Path(__file__).resolve().parent
code = (root / "ProcesarExcel.vb").read_text(encoding="utf-8")
code_attribute = quoteattr(code.replace("\r\n", "\n"))
load_code = (root / "CargarOdoo.vb").read_text(encoding="utf-8")
load_code_attribute = quoteattr(load_code.replace("\r\n", "\n"))

xaml = f'''<Activity mc:Ignorable="sap sap2010" x:Class="Main" mva:VisualBasic.Settings="{{x:Null}}"
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  xmlns:mva="clr-namespace:Microsoft.VisualBasic.Activities;assembly=System.Activities"
  xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"
  xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
  xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib"
  xmlns:sco="clr-namespace:System.Collections.ObjectModel;assembly=mscorlib"
  xmlns:ui="http://schemas.uipath.com/workflow/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <TextExpression.NamespacesForImplementation>
    <sco:Collection x:TypeArguments="x:String">
      <x:String>System</x:String>
      <x:String>System.Activities</x:String>
      <x:String>System.Activities.Statements</x:String>
      <x:String>System.Collections</x:String>
      <x:String>System.Collections.Generic</x:String>
      <x:String>System.Data</x:String>
      <x:String>System.IO</x:String>
      <x:String>System.Linq</x:String>
      <x:String>System.Web.Script.Serialization</x:String>
      <x:String>System.Security.Cryptography</x:String>
      <x:String>Microsoft.Office.Interop.Excel</x:String>
      <x:String>Microsoft.VisualBasic</x:String>
      <x:String>UiPath.Core</x:String>
      <x:String>UiPath.Core.Activities</x:String>
    </sco:Collection>
  </TextExpression.NamespacesForImplementation>
  <TextExpression.ReferencesForImplementation>
    <sco:Collection x:TypeArguments="AssemblyReference">
      <AssemblyReference>mscorlib</AssemblyReference>
      <AssemblyReference>System</AssemblyReference>
      <AssemblyReference>System.Core</AssemblyReference>
      <AssemblyReference>System.Activities</AssemblyReference>
      <AssemblyReference>System.Data</AssemblyReference>
      <AssemblyReference>System.Web.Extensions</AssemblyReference>
      <AssemblyReference>System.Security</AssemblyReference>
      <AssemblyReference>Microsoft.VisualBasic</AssemblyReference>
      <AssemblyReference>UiPath.System.Activities</AssemblyReference>
      <AssemblyReference>Microsoft.Office.Interop.Excel</AssemblyReference>
      <AssemblyReference>Office</AssemblyReference>
    </sco:Collection>
  </TextExpression.ReferencesForImplementation>
  <Sequence DisplayName="Validar libros Excel (solo lectura)">
    <ui:InvokeCode DisplayName="Recorrer, validar y reportar Excel" Language="VBNet" Code={code_attribute}>
      <ui:InvokeCode.Arguments>
        <scg:Dictionary x:TypeArguments="x:String, Argument" />
      </ui:InvokeCode.Arguments>
    </ui:InvokeCode>
    <ui:InvokeCode DisplayName="Verificar conexion o cargar datos segun RPA_MODO" Language="VBNet" Code={load_code_attribute}>
      <ui:InvokeCode.Arguments>
        <scg:Dictionary x:TypeArguments="x:String, Argument" />
      </ui:InvokeCode.Arguments>
    </ui:InvokeCode>
  </Sequence>
</Activity>
'''

(root / "Main.xaml").write_text(xaml, encoding="utf-8")
