import enum as _enum
import io as _io
import typing as _typing

from lxml import etree as _etree

XML_ENCODING = "UTF-8"
XML_DOCTYPE = "<!DOCTYPE BrickStockXML>"
XML_ROOT_TAG = "BrickStockXML"

OBJ_GUISTATES = "GuiStates"


def _enum_ensurer(enumtype: _enum.EnumMeta
) -> _typing.Callable[[_enum.Enum], str]:
  return lambda v: enumtype(v).value


def _is_binary(fp: _typing.io) -> bool:
  # https://stackoverflow.com/a/44584871/2334951
  if hasattr(fp, "mode"):
    return "b" in f.mode
  else:
    return isinstance(fp, (_io.RawIOBase, _io.BufferedIOBase))


class Condition(_enum.Enum):
  # taken from BrickStock source
  # (bricklink.h #254; bricklink.cpp #989..)
  NEW = "N"
  USED = "U"


class SubCondition(_enum.Enum):
  # taken from BrickStock source
  # (bricklink.h #255; bricklink.cpp #991..)
  NONE = "?"
  COMPLETE = "C"
  INCOMPLETE = "I"
  MISB = "M"


class Status(_enum.Enum):
  # taken from BrickStock source
  # (bricklink.h #316; bricklink.cpp #1019..)
  INCLUDE = "I"
  EXCLUDE = "X"
  EXTRA = "E"
  UNKNOWN = "?"


class RootChildren(_enum.Enum):
  INVENTORY = "Inventory"
  GUISTATE = "GuiState"


class InventoryChildren(_enum.Enum):
  ITEM = "Item"


class ItemChildren(_enum.Enum):
  # taken from BrickStock source (bricklink.cpp #1124..)
  ITEMID = "ItemID"
  ITEMTYPEID = "ItemTypeID"
  COLORID = "ColorID"
  ITEMNAME = "ItemName"
  ITEMTYPENAME = "ItemTypeName"
  COLORNAME = "ColorName"
  CATEGORYID = "CategoryID"
  CATEGORYNAME = "CategoryName"
  STATUS = "Status"
  QTY = "Qty"
  PRICE = "Price"
  CONDITION = "Condition"
  SUBCONDITION = "SubCondition"
  ALTERNATE = "Alternate"  # not suppoerted by BrickStore
  COUNTERPART = "Counterpart"  # not suppoerted by BrickStore
  IMAGE = "Image"
  BULK = "Bulk"
  SALE = "Sale"
  COMMENTS = "Comments"
  REMARKS = "Remarks"
  RETAIN = "Retain"
  STOCKROOM = "StockRoom"
  RESERVED = "Reserved"
  LOTID = "LotID"
  TQ1 = "TQ1"
  TP1 = "TP1"
  TQ2 = "TQ2"
  TP2 = "TP2"
  TQ3 = "TQ3"
  TP3 = "TP3"
  TOTALWEIGHT = "TotalWeight"
  ORIGPRICE = "OrigPrice"
  ORIGQTY = "OrigQty"


itemchildrencast = {
  ItemChildren.COLORID: int,
  ItemChildren.CATEGORYID: int,
  ItemChildren.STATUS: _enum_ensurer(Status),
  ItemChildren.QTY: int,
  ItemChildren.PRICE: float,
  ItemChildren.CONDITION: _enum_ensurer(Condition),
  ItemChildren.SUBCONDITION: _enum_ensurer(SubCondition),
  ItemChildren.ALTERNATE: bool,
  ItemChildren.COUNTERPART: bool,
  ItemChildren.BULK: int,
  ItemChildren.SALE: int,
  ItemChildren.RETAIN: bool,
  ItemChildren.STOCKROOM: bool,
  ItemChildren.LOTID: int,
  ItemChildren.TQ1: int,
  ItemChildren.TP1: float,
  ItemChildren.TQ2: int,
  ItemChildren.TP2: float,
  ItemChildren.TQ3: int,
  ItemChildren.TP3: float,
  ItemChildren.ORIGPRICE: float,
  ItemChildren.ORIGQTY: int,
}


class GuiStateAttribute(_enum.Enum):
  APPLICATION = "Application"
  VERSION = "Version"


class GuiStateChildren(_enum.Enum):
  ITEMVIEW = "ItemView"


class ItemViewChildren(_enum.Enum):
  COLUMNORDER = "ColumnOrder"
  COLUMNWIDTHS = "ColumnWidths"
  COLUMNWIDTHSHIDDEN = "ColumnWidthsHidden"
  SORTCOLUMN = "SortColumn"
  SORTDIRECTION = "SortDirection"


class Field(_enum.IntEnum):
  # taken from BrickStock source (cdocument.h #44..)
  Status = 0
  Picture = 1
  PartNo = 2
  Description = 3
  Condition = 4
  Color = 5
  Quantity = 6
  Price = 7
  Total = 8
  Bulk = 9
  Sale = 10
  Comments = 11
  Remarks = 12
  Category = 13
  ItemType = 14
  TierQ1 = 15
  TierP1 = 16
  TierQ2 = 17
  TierP2 = 18
  TierQ3 = 19
  TierP3 = 20
  LotId = 21
  Retain = 22
  Stockroom = 23
  Reserved = 24
  Weight = 25
  YearReleased = 26
  QuantityOrig = 27
  QuantityDiff = 28
  PriceOrig = 29
  PriceDiff = 30


class SortDirection(_enum.Enum):
  Ascending = "A"
  Descending = "D"


def dump(obj: dict, fp: _typing.io, *,
    pretty_print = True,
) -> None:
  s = dumps(obj, pretty_print = pretty_print)
  if _is_binary(fp):
    return fp.write(skip_decode = True)
  else:
    return fp.write(s)


def dumps(obj: dict, *,
    pretty_print = True,
    skip_decode = False,
) -> _typing.Union[str, bytes]:
  root = obj2root(obj)
  b = etree.tostring(
      root,
      pretty_print = pretty_print,
      xml_declaration = True,
      encoding = XML_ENCODING,
      doctype = XML_DOCTYPE,
  )
  if skip_decode:
    return b
  else:
    s = b.decode(XML_ENCODING)
    return s


def load(fp: _typing.io) -> dict:
  tree = _etree.parse(fp)
  root = tree.getroot()
  return root2obj(root)


def loads(s: str) -> dict:
  try:
    root = _etree.fromstring(s)
  except ValueError:
    root = _etree.fromstring(s.encode(XML_ENCODING))
  return root2obj(root)


def obj2root(obj: dict) -> _etree.Element:
  root = _etree.Element(XML_ROOT_TAG)
  inventory_o = obj.get(RootChildren.INVENTORY.value)
  if inventory_o:
    inventory_e = inventory_o2e(inventory_o)
    root.append(inventory_e)
  for guistate_o in obj.get(OBJ_GUISTATES, []):
    root.append(guistate_o2e(guistate_o))
  return root


def root2obj(root: _etree.Element) -> dict:
  result = {}
  inventory_e = root.find(RootChildren.INVENTORY.value)
  if inventory_e is not None:
    inventory_o = inventory_e2o(inventory_e)
    if inventory_o:
      result[RootChildren.INVENTORY.value] = inventory_o
  guistate_seq = root.findall(RootChildren.GUISTATE.value)
  if guistate_seq:
    guistate_o_seq = []
    for guistate_e in guistate_seq:
      guistate_o = guistate_e2o(guistate_e)
      if guistate_o:
        guistate_o_seq.append(guistate_o)
    if guistate_o_seq:
      result[OBJ_GUISTATES] = guistate_o_seq
  return result


def inventory_e2o(inventory_e: _etree.Element) -> list:
  result = []
  for item_e in inventory_e:
    item_o = {}
    for property_tag in ItemChildren.__members__.values():
      property_name = property_tag.value
      property_e = item_e.find(property_name)
      if property_e is not None:
        cast_func = itemchildrencast.get(property_tag, str)
        if cast_func is bool:
          item_o[property_name] = True
        else:
          property_v = cast_func(property_e.text)
          item_o[property_name] = property_v
    if item_o:
      result.append(item_o)
  return result


def inventory_o2e(inventory_o: dict) -> _etree.Element:
  result = _etree.Element(RootChildren.INVENTORY.value)
  for item_o in inventory_o:
    item_e = _etree.Element(InventoryChildren.ITEM.value)
    result.append(item_e)
    for property_tag in ItemChildren.__members__.values():
      property_v = item_o.get(property_tag.value)
      if property_v is None:
        continue
      cast_func = itemchildrencast.get(property_tag, str)
      if cast_func is bool and not property_v:
        continue
      property_e = _etree.Element(property_tag.value)
      item_e.append(property_e)
      if cast_func is not bool:
        property_e.text = str(cast_func(property_v))
  return result


def guistate_e2o(guistate_e: _etree.Element) -> dict:
  result = {}
  for prop in GuiStateAttribute.__members__.values():
    if prop.value in guistate_e.attrib:
      result[prop.value] = guistate_e.attrib[prop.value]
  for e1 in guistate_e.iterchildren():
    e1name = GuiStateChildren(e1.tag)
    if e1name is GuiStateChildren.ITEMVIEW:
      itemview_o = {}
      for e2 in e1.iterchildren():
        e2name = ItemViewChildren(e2.tag)
        if e2name is ItemViewChildren.COLUMNORDER:
          columorder_o = [
            Field(int(s)).name
            for s in e2.text.split(",")
          ]
          itemview_o[e2name.value] = columorder_o
        elif e2name in (
            ItemViewChildren.COLUMNWIDTHS,
            ItemViewChildren.COLUMNWIDTHSHIDDEN,
        ):
          widths_o = {name: 0 for name in Field.__members__}
          for i, s in enumerate(e2.text.split(",")):
            widths_o[Field(i).name] = int(s)
          itemview_o[e2name.value] = widths_o
        elif e2name is ItemViewChildren.SORTCOLUMN:
          itemview_o[e2name.value] = Field(int(e2.text)).name
        elif e2name is ItemViewChildren.SORTDIRECTION:
          f_ensure = _enum_ensurer(SortDirection)
          itemview_o[e2name.value] = f_ensure(e2.text)
      if itemview_o:
        result[e1name.value] = itemview_o
  return result


def guistate_o2e(guistate_o: dict) -> _etree.Element:
  result = _etree.Element(RootChildren.GUISTATE.value)
  for attribname in GuiStateAttribute.__members__.values():
    if attribname.value in guistate_o:
      value = guistate_o[attribname.value]
      if value:
        result.attrib[attribname.value] = str(value)
  for e1name in GuiStateChildren.__members__.values():
    if e1name.value not in guistate_o:
      continue
    obj1 = guistate_o[e1name.value]
    e1 = _etree.Element(e1name.value)
    result.append(e1)
    if e1name is GuiStateChildren.ITEMVIEW:
      columnwidths_key = ItemViewChildren.COLUMNWIDTHS.value
      columswidths_obj = obj1.get(columnwidths_key, {})
      for e2name in ItemViewChildren.__members__.values():
        if e2name.value not in obj1:
          continue
        obj2 = obj1[e2name.value]
        e2 = _etree.Element(e2name.value)
        e1.append(e2)
        if e2name is ItemViewChildren.COLUMNORDER:
          e2.text = ",".join(
              str(int(Field[name])) for name in obj2
          )
        elif e2name in (
            ItemViewChildren.COLUMNWIDTHS,
            ItemViewChildren.COLUMNWIDTHSHIDDEN,
        ):
          vals2 = []
          for field in Field.__members__.values():
            val2 = obj2.get(field.name)
            if val2 is None:
              if e2name is ItemViewChildren.COLUMNWIDTHSHIDDEN:
                val2 = columswidths_obj.get(field.name, 0)
              else:
                val2 = 0
            vals2.append(val2)
          e2.text = ",".join(str(int(v)) for v in vals2)
        elif e2name is ItemViewChildren.SORTCOLUMN:
          e2.text = str(int(Field[obj2]))
        elif e2name is ItemViewChildren.SORTDIRECTION:
          f_ensure = _enum_ensurer(SortDirection)
          e2.text = f_ensure(obj2)
        else:
          e2.text = str(obj2)
  return result
