// 日付が指定されている祝日
var DateHoliday = function( month, day ){
  this.month = month;
  this.day = day;
};
DateHoliday.prototype = {
  getHoliday:  function(year){
    return this.day;
  }
};

// ハッピーマンデー
var MondayHoliday = function( month, week ){
  this.month = month;
  this.week = week;
  this.wday = 1;
};
MondayHoliday.prototype = {
  getHoliday: function(year){
    var firstWday = new Date(year,this.month-1,1).getDay();
    return 7*(this.week - ( (firstWday <= this.wday) ? 1 : 0 )) + ( this.wday - firstWday ) + 1; // 第this.week this.wday曜日
  }
};

// 春分・秋分の日
var EquinoxHoliday = function( month ){
  this.month = month;
  if( this.month == 3 )
    this.offset = 20.8431;
  else if ( this.month == 9 )
    this.offset = 23.2488;
  else
    throw 'Not exists equinox day in '+month;
};
EquinoxHoliday.prototype = {
  getHoliday: function(year){
    return Math.floor(this.offset+0.242194*(year-1980)-Math.floor((year-1980)/4)); // 1980-2099に対応?
  }
};

var HolidayHelper = {
  holidayMap: {
    1: [new DateHoliday( 1, 1 ), new MondayHoliday( 1, 2 )],
    2: [new DateHoliday( 2, 11 )],
    3: [new EquinoxHoliday( 3 )],
    4: [new DateHoliday( 4, 29 )],
    5: [new DateHoliday( 5, 3 ), new DateHoliday( 5, 4 ), new DateHoliday( 5, 5 )],
    7: [new MondayHoliday( 7, 3 )], 
    9: [new MondayHoliday( 9, 3 ), new EquinoxHoliday( 9 )],
    10: [new MondayHoliday( 10, 2 )],
    11: [new DateHoliday( 11, 3 ), new DateHoliday( 11, 23 )],
    12: [new DateHoliday( 12, 23 )]
  },
  // 月をまたがる振替休日や国民の休日(昨日と翌日が国民の祝日である日)が存在しないことを前提とした処理
  getHolidays: function( year, month ){
    var holidays = this.holidayMap[month];
    if( !holidays )
      return {};
    var dayHash= {}
    var dateArray = []
    for( var i=0, len=holidays.length; i<len; i++ ){
      var day = holidays[i].getHoliday(year);
      dayHash[ day ] = true;
      dateArray.push( new Date(year,month-1,day) );
    }

    for( var i=0, len=dateArray.length; i<len; i++ ){
      var date = dateArray[i];
      var day = date.getDate();

      if( date.getDay() == 0 ){
        var cday = day+1;
        while( dayHash[cday] )  // 振替休日が祝日の場合、翌日へ
          cday++;
        dayHash[ cday ] = true;
      }
      // 国民の休日判定には、振替休日を考慮しない
      if( dayHash[day+2] && !dayHash[day+1] )
        dayHash[ day+1 ] = true;
    }
    return dayHash;
  },
  isHoliday : function( dateOrYear, month, day ){
    var year = day ? dateOrYear : dateOrYear.getFullYear();
    var month = day ? month : dateOrYear.getMonth()+1;
    var day = day || dateOrYear.getDate();

    return !! this.getHolidays( year, month )[ day ];
  }
};
