var checkout_json = {
  'plan':{},
  'minutes':{},
  'agent':{},
  'recording':{},
};
var plan_product_id = null;

function get_num(num){
  return num.replace(/,/g, '').replace('$', '')
}


function fix_int_row(row_class){
  var row = $(row_class);
  var item_total = 0;

  var num = get_num(row.find('.item_included').html());
  if(num != '-')
    item_total += Number(num);

  num = get_num(row.find('.item_added').html());
  if(num != '-')
    item_total += Number(num);

  num = get_num(row.find('.item_bonus').html());
  if(num != '-')
    item_total += Number(num);

  row.find('.item_total').html(item_total);
}

function plan_click(product_id, action_for='add', qty=null){
  if(disabled_plan_products.includes(product_id)){
    alert('Contact Prashant for plan type changes');
    return
  }

  console.log(qty);
  if(qty == null){
    qty = Number($(".for_plan").find('.item_added_qty').val());
  } else {
    qty = Number(qty);
    $(".for_plan").find('.item_added_qty').val(qty);
  }

  var class_name = '.plan_'+product_id;

  $(".card").removeClass("plan_selected");
  $(class_name).addClass('plan_selected');

  var id = $(class_name).data("id");
  var amount = $(class_name).data("amount");
  // var min_qty = $(class_name).data("min_qty");
  var description = $(class_name).data("description");

  $(".product_name").html(description);

  // $(".for_plan").find('.item_added_qty').attr({
  //      "min" : min_qty
  // });

  // qty = Math.max(qty, min_qty);
  // $(".for_plan").find('.item_added_qty').val(qty);

  checkout_json['plan'] = {}
  checkout_json['plan'][id] = {"qty":qty};
  plan_product_id = id;


  // $(".for_plan").find('.item_added').html(qty);
  // fix_int_row(".for_plan");
  $(".for_plan").find('.item_amount').html(amount*qty);

  change_total_amount();
}

function change_total_amount(){
  format_quantity();
  format_currency();

  let sum = 0;
  $("td.item_amount").each(function() {
    num = get_num($(this).html());

    if(num != '-'){
      sum += Number(num);
    }

  });

  $(".total").html(sum);

  // var gst = sum * 0.18
  // $("#gst").html(gst);
  //
  // sum += gst;
  // sum = "$".concat(sum);
  $(".balance_due").html(sum);

  // console.log(checkout_json);

  format_currency_sum();
}

function number_to_comma(number) {
  if(number == '-')
    return '-'
  number = get_num(number);
  new_num = Number(number).toLocaleString('en-IN', {maximumFractionDigits:0});
  if(new_num == '0')
    return '-'
  return new_num
}

function float_to_comma(number) {
  number = get_num(number);
  if(number == '-')
    return '-'

  new_num = Number(number).toLocaleString('en-IN', {maximumFractionDigits:2, minimumFractionDigits: 2});
  if(new_num == '0.00')
    return '-'
  return "$".concat(new_num)
}

function format_currency() {
  $("td.currency").each(function() {
    num = get_num($(this).html());
    $(this).html(float_to_comma(num));
    // $(this).html("$".concat(float_to_comma(num)));
  });
}

function format_currency_sum() {
  $(".currency_sum").each(function() {
    num = get_num($(this).html());
    $(this).html(float_to_comma(num));
    // $(this).html("$".concat(float_to_comma(num)));
  });
}

function format_quantity() {
  $("td.quantity").each(function() {
    num = get_num($(this).html());
    if(['True', 'False'].includes(num) == false){
      var new_num = number_to_comma(num);
      $(this).html(new_num);
    }
  });
}


$("#form button").click(function (e) {
  e.preventDefault();

  checkout_json['submit'] = $(this).attr("value");

  let csrftoken = $("input[name=csrfmiddlewaretoken]").val();

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      // if not safe, set csrftoken
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    },
  });

  $.ajax({
    type: 'POST',
    contentType: 'application/json; charset=utf-8',
    data: JSON.stringify(checkout_json),
    dataType: 'json',
    success: function(data) {
      console.log(data);
      if(data.success == true){
        if(data.next){
          window.location.href = data.next; // redirect payment page
        } else {
          location.reload();
        }

      }
    },
    error: function(data) {
      console.log(data);
    }
  });
});


function change_plan_qty(qty){
  plan_click(plan_product_id, 'add', qty=qty);
}
