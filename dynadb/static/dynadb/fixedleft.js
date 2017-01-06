
$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };

 $(document).on('click',"[id='left']",function(){
  //   $("[id='left']").click(function(){
         var leftpanel=$(this);
         var rightpanel=$("[id='pmolform']");
         leftpanel.removeAttr('data-spy');
         leftpanel.attr('class',"col-md-12");
       //  rightpanel.attr('data-spy',"affix");
       //  rightpanel.attr('class',"col-md-7 ");
       //  rightpanel.attr('style',"position:absolute;left:36%;width:665px");
       });

 //   $("[id='left']").mouseout(function(){
     //      var leftpanel=$(this);
     //      var rightpanel=$("[id='pmolform']");
     //      leftpanel.attr('data-spy',"affix");
   //      leftpanel.attr('class',"col-md-12 affix");
       //  rightpanel.removeAttr('style');
     //    rightpanel.removeAttr('data-spy');
    //    rightpanel.attr('class',"col-md-7");
   // });
});
