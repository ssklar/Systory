#!/usr/bin/perl -wT
###############################################################################
#### index.cgi
#### $Id: index.cgi,v 1.19 2004/03/07 19:11:34 ssklar Exp ssklar $
###############################################################################

use strict;
use CGI ':standard';
use CGI::Carp 'fatalsToBrowser';
use RRDs;

###############################################################################

my $basedir        = "/opt/home/systory";
my $groupdir       = "$basedir/group";
my $datadir        = "$basedir/host";

###############################################################################

my %stats = (  
	cpu   => "CPU",
	load  => "LOAD",
	swap  => "SWAP"
);

my %spans = (  
	day     =>   "86400",
	twodays =>   "172800",
	week    =>   "604800",
	twoweeks =>  "1209600",
	month   =>   "2592000",
	sixmonths => "15552000",
	year    =>   "31536000"
);

my %spans_pretty = (  
	'86400'   => "last day",
	'172800'   => "last two days",
	'604800'   => "last week",
	'1209600'  => "last two weeks",
	'2592000'  => "last month",
	'15552000' => "last six months",
	'31536000' => "last year"
);

###############################################################################

## main

my ($group, @hosts, @stats, @spans, @notes);

&determine_hosts;
&determine_stats;
&determine_spans;

&print_page_top;

if (defined (param('graph')) || defined (param('g'))) {	

	&generate_graphs
		
} else { 
		
	&generate_index
		
};

if (scalar(@notes) > 0) {

	print "<BR><BLOCKQUOTE>";
	print @notes;
	print "</BLOCKQUOTE></BR>";
};

&print_page_bottom;

exit 0;

## END main

###############################################################################

sub note {

	## formats an message for proper presentation in the webpage and 
	## pushes it onto the @notes array.
	
	my $message = join (" ", @_);
	
	push (@notes, $message . "<br>\n");
	
};  ## END sub note

###############################################################################

sub print_page_top {

	my $title = "systory";
	
	if    ($group)               { $title .= " | group: $group" } 
	elsif (scalar (@hosts) >= 1) { $title .= " | host: $hosts[0]" };
	
	if (defined (param('graph')) || defined (param('g'))) {

		if (scalar (@stats) == 1)    { $title .= " | stat: $stats[0]" }
		elsif (scalar (@stats) > 1)  { $title .= " | stats: multiple" };
		
		if (scalar (@spans) == 1)    { $title .= " | span: $spans_pretty{$spans[0]}" }
		elsif (scalar (@spans) > 1)  { $title .= " | spans: multiple" };
		
	};

	if ( defined (param('print'))) {

		print header (
		  -type    => "text/html",
		  -expires => "+10m"
		);
		
	
		print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
			   <HTML>
			   <HEAD>';
			   
		print "<TITLE>$title</TITLE>";
		
		print '<LINK REL="StyleSheet" HREF="style.css" TYPE="text/css">
			   <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=iso-8859-1">
			   </HEAD>';
	
		
		print '<BODY MARGINHEIGHT="12" MARGINWIDTH="12" TOPMARGIN="12" LEFTMARGIN="12">
			   <A NAME="top"></A>
			   <TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
			   <TR VALIGN="top">
			   <TD><IMG SRC="spacer.gif" ALT="" WIDTH="185" HEIGHT="2" BORDER="0"> </TD>
			   <TD VALIGN="bottom" WIDTH="100%">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="428" HEIGHT="2" BORDER="0"></TD>
			   <TD ROWSPAN="2" ALIGN="right">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="2" BORDER="0">
			   </TD></TR>
			   <TR VALIGN="top"><TD COLSPAN="3" BGCOLOR="#000000" WIDTH="100%">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="2" HEIGHT="1" BORDER="0">
			   </TD></TR></TABLE>';
		
		print '<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
			   <TR VALIGN="top"><TD VALIGN="top" WIDTH="40">
			   <TD WIDTH="40" BGCOLOR="#FFFFFF">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="15" BORDER="0">
			   </TD><TD><IMG SRC="spacer.gif" ALT="" WIDTH="20" HEIGHT="15" BORDER="0">
			   </TD><TD WIDTH="100%" BGCOLOR="#EFEEED" VALIGN="top">';
	
		return
		
	} else {
	
		opendir (GROUPDIR, $groupdir) ||
			die "Fatal: can't open groupdir $groupdir: $!";
			
		my @groups = sort (grep { -f "$groupdir/$_" && /^\w+/ } readdir (GROUPDIR));
		
		closedir GROUPDIR;
		
		print header (
		  -type    => "text/html",
		  -expires => "+10m"
		);
		
	
		print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
			   <HTML>
			   <HEAD>';
			   
		print "<TITLE>$title</TITLE>";
		
		print '<LINK REL="StyleSheet" HREF="style.css" TYPE="text/css">
			   <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=iso-8859-1">
			   </HEAD>';
	
		
		print '<BODY MARGINHEIGHT="12" MARGINWIDTH="12" TOPMARGIN="12" LEFTMARGIN="12">
			   <A NAME="top"></A>
			   <TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
			   <TR VALIGN="top">
			   <TD><IMG SRC="spacer.gif" ALT="" WIDTH="185" HEIGHT="2" BORDER="0"> </TD>
			   <TD VALIGN="bottom" WIDTH="100%">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="428" HEIGHT="2" BORDER="0"></TD>
			   <TD ROWSPAN="2" ALIGN="right">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="2" BORDER="0">
			   </TD></TR>
			   <TR VALIGN="top"><TD COLSPAN="3" BGCOLOR="#000000" WIDTH="100%">
			   <IMG SRC="spacer.gif" ALT="" WIDTH="2" HEIGHT="1" BORDER="0">
			   </TD></TR></TABLE>';
		
		print '<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
			   <TR VALIGN="top"><TD VALIGN="top" WIDTH="150">';
			   
		print '<A HREF="index.cgi"><DIV ALIGN="center"><H1>systory</H1></DIV></A>';
		
		print '<P CLASS="smallest"> Click on a host name from the table on the right to view all statistics for all time spans<B><I> or </I></B>Check one or more hosts and/or one or more groups, one or more statistics, and one or more time spans.</P>'; 
		
		#### here goes the form elements
		
		print '<FORM METHOD="get" TARGET="_blank">';
		
		print '<INPUT TYPE="hidden" NAME="g">';
		
		####  the "group" selection menu ...
		
		print '<H5>group:</H5>';
		print '<SELECT NAME="group" SIZE="5" MULTIPLE>';
		print '<OPTION VALUE="all">all</OPTION>';
		print '<OPTION VALUE="">----------------</OPTION>';
		
		foreach (@groups) { print "<OPTION VALUE=\"$_\">$_</OPTION>" };
	
		print '</SELECT>';
		
		####  the "stat" selection menu ...
		
		print '<H5>stat:</H5>';
		print '<SELECT NAME="stat" SIZE="5" MULTIPLE>';
		print '<OPTION VALUE="all">all</OPTION>';
		print '<OPTION VALUE="">----------------</OPTION>';
		
		foreach (sort keys (%stats)) { print "<OPTION VALUE=\"$stats{$_}\">$_</OPTION>" };
		
		print '</SELECT>';
		
		####  the "span" selection menu ...
		
		print '<H5>span:</H5>';
		print '<SELECT NAME="span" SIZE="5" MULTIPLE>';
		print '<OPTION VALUE="all">all</OPTION>' . "\n";
		print '<OPTION VALUE="">----------------</OPTION>';
	
		foreach (sort keys (%spans)) { print "<OPTION VALUE=\"$_\">$spans_pretty{$spans{$_}}</OPTION>" };
		
		print '</SELECT>';
		
		####  the graph size selection ...
		
		print '<H5>graph size:</H5>';
		print '<INPUT TYPE="radio" NAME="gsize" VALUE="small"><SPAN CLASS="smaller"> small </INPUT><BR>';
		print '<INPUT TYPE="radio" NAME="gsize" VALUE="" CHECKED><SPAN CLASS="smaller"> medium </INPUT><BR>';
		print '<INPUT TYPE="radio" NAME="gsize" VALUE="large"><SPAN CLASS="smaller"> large </INPUT><BR>';
	
		####  the printer-friendly checkbox ...
		
		print '<BR><INPUT TYPE="checkbox" NAME="print" VALUE="true"><SPAN CLASS="smaller"> <B>printer friendly</B>
		       <BR><SPAN CLASS="smallest">(no selection form)</SPAN></INPUT><BR>';
	
		####  the "submit" button ...
		
		print '<BR><DIV ALIGN="center"><INPUT TYPE="submit" VALUE=" generate page "></INPUT><BR>
			   <BR><INPUT TYPE="reset"  VALUE=" reset selections "></INPUT></DIV><BR><BR>';
		
			
		#print "<h3>param dump:</h3>\n";
		#print CGI::dump();
	
		
		print '</TD>
			   <TD><IMG SRC="spacer.gif" ALT="" WIDTH="20" HEIGHT="15" BORDER="0">
			   </TD><TD WIDTH="100%" BGCOLOR="#EFEEED" VALIGN="top">';
	
		return
		
	};

};  ## END print_page_top

###############################################################################

sub determine_hosts {

	if (param('group') =~ /^all$/i) {
	
		param(-name => 'host', -value => 'all');
		
	};
	
	unless (param('host') || param('group')) {
	
		param(-name => 'host',  -value => 'all');
		param(-name => 'group', -value => 'all');
		
		$group = "all";
		
	};
	
	if (param('host')) {
	
		foreach (param('host')) {
		
			if ($_ =~ /^all$/i) {
			
				opendir (DATADIR, $datadir) ||
					die "Can't open datadir $datadir: $!";
					
				@hosts = sort (grep { -d "$datadir/$_" && /^\w+/ } readdir (DATADIR));
	
				closedir DATADIR;
				
			} elsif (-d "$datadir/$_" && $_ =~ /(^\w.+$)/) {
			
				push (@hosts, $1)
				
			} else {
			
				note ("Invalid host $_ specified.");			
			};
			
		};
		
	} elsif (param('group') && param('group') =~ /(^\w+.*)/) {
	
		$group = "$1";
				
		if (-f "$groupdir/$group") {
						
			open (GROUPFILE, "$groupdir/$group") ||
				die "Can't read group file $groupdir/$group: $!";
				
			while (<GROUPFILE>) {
			
					next if /^$/;
					
					chomp;
					
					if (-d "$datadir/$_") {
					
						push (@hosts, $_);
						
					} else {
					
						note ("No data available for host $_ in group $group.");
						
					};
			};
			
			close GROUPFILE;

		} else {
		
			note ("Invalid group $group specified.");
		
		};
		
		my @hosts_sorted = sort {$::a cmp $::b} @hosts;
		
		@hosts = @hosts_sorted;
		
	};
	

};  ## END determine_hosts

###############################################################################

sub generate_index {

	print <<END;
	  <table align="center" width="98%" cellpadding="6" cellspacing="0" border="0">
        <tr>
          <TD ALIGN="left" VALIGN="middle"></TD>
          <td align="left" valign="middle"><H5>Host</H5></td>
          <td align="left" valign="middle"><H5>OS</H5></td>
          <td align="left" valign="middle"><H5>Model</H5></td>
          <td align="left" valign="middle"><H5>CPUs</H5></td>
          <td align="left" valign="middle"><H5>RAM (MB)</H5></td>
          <td align="left" valign="middle"><H5>Uptime</H5></td>
          <td align="left" valign="middle"><H5>Last Update</H5></td>
        </tr>
END
	my $hostindex = "0";
	
	my $rowcolor;
	
	foreach (@hosts) {
		
		open(SUMMARY, "$datadir/$_/summary") ||
			do { note "no summary found for host $_" ; next };
			
		my $age = sprintf ("%d", time() - (sub { $_[9] } -> (stat SUMMARY)));
		
		$age = ($age > 86399) ? "<FONT COLOR='#FF0000'>" . sprintf ("%d", $age / 86400) . " d</FONT>" :
		       ($age >  3549) ? "<FONT COLOR='#FF0000'>" . sprintf ("%d", $age /  3600) . " h</FONT>" :
		       ($age >   601) ? "<FONT COLOR='#FF0000'>" . sprintf ("%d", $age /   600) . " m</FONT>" :
		       ($age >   300) ? "<FONT COLOR='#FF0000'>" . sprintf ("%d", $age        ) . " s</FONT>" :
		                        $age . " s";

		my ($host, $os, $model, $proc_info, $ram, $uptime) = split (/\|/, (<SUMMARY>));
		
		$hostindex++;
						
		if ($hostindex % 2) {
		
			$rowcolor = "#FFFFFF"
			
		} else {
		
			$rowcolor = "#EFEEED"
			
		};

		print "<TR VALIGN='top' BGCOLOR=\"$rowcolor\">\n";
		print '<TD><INPUT TYPE="checkbox" NAME="host" VALUE="' . $host . '"></INPUT></TD>';
		print "<TD><A HREF='?g=&host=" . $host . "'>" . $host . "</A></TD>
		       <TD>$os</TD>
		       <TD>$model</TD>
		       <TD>$proc_info</TD>
		       <TD>$ram</TD>
		       <TD>$uptime</TD>
		       <TD>$age</TD></TR>\n";

		close SUMMARY;
		
	};
	
	print "<TR><TD COLSPAN='7'>&nbsp;</TD></TR>\n";
	
	print "</TABLE>\n";

}  ## END generate_index

###############################################################################

sub determine_stats {

	unless (param('stat')) {
	
		param(-name => 'stat', -value => 'all')
		
	};
	
	foreach (param('stat')) {
	
		if ($_ =~ /^all$/i) {
		
			foreach (keys (%stats)) {
			
				push (@stats, $stats{$_});
				
			};
	
		} elsif (exists ($stats{"\L$_"}) && $_ =~ /^(\w+)$/) {
		
			push (@stats, $stats{"\L$1"})
			
		} else {
		
			note ("Invalid stat $_ specified.");
			
		};
	
	};

}  ## END determine_stats

###############################################################################

sub determine_spans {

	unless (param('span')) {
	
		param(-name => 'span', -value => 'all')
		
	};
	
	foreach (param('span')) {
	
		if ($_ =~ /^all$/i) {
		
			foreach (keys (%spans)) {
			
				push (@spans, $spans{$_});
				
			};
			
		} elsif (exists ($spans{"\L$_"}) && $_ =~ /^(\w+)$/) {
		
			push (@spans, $spans{"\L$_"})
			
		} else {
		
			note ("Invalid span $_ specified.");
			
		};

	};
	
	my @spans_sorted = sort {$::a <=> $::b} @spans;
	
	@spans = @spans_sorted;

}  ## END determine_spans

###############################################################################

sub generate_graphs {

	print '<TABLE ALIGN="center" WIDTH="96%" CELLPADDING="0" CELLSPACING="8" BORDER="0">';


	my @graph_common_args = (
		"--lazy",
		"--no-minor",
		"--lower-limit", "0",
		"--color", "BACK#FFFFFF",
		"--color", "CANVAS#FFFFFF",
		"--color", "MGRID#666666",
		"--color", "SHADEA#FFFFFF",
		"--color", "SHADEB#FFFFFF"
	);

	my $gsize;
	
	if (param('gsize') =~ /^sm/i) {
	
		push (@graph_common_args, "--width", "400", "--height", "100");
		$gsize = "small";
		
	} elsif (param('gsize') =~ /^la/i)  {
	
		push (@graph_common_args, "--width", "800", "--height", "200");
		$gsize = "large";
		
	} else {
	
		push (@graph_common_args, "--width", "600", "--height", "150");
		$gsize = "medium";
		
	};

	my @graph_args;
	
		foreach my $host (@hosts) {
		
			print "<!-- start of host $host --> \n";
			print "<TR><TD BGCOLOR='#EFEEED'><A HREF='index.cgi?graph=&span=all&stat=all&host=" . $host . "'><H3>$host</H3></A></TD>";
			print "<TD BGCOLOR='#EFEEED' ALIGN='right' VALIGN='top'><A HREF='#top'>top</A></TD></TR>";
			
						
			foreach my $span (@spans) {
			
				print "<TR><TD BGCOLOR='#EFEEED' COLSPAN='2' ALIGN='center'>";

				print "<H5 ALIGN='left'>$spans_pretty{$span}</H5>\n";
				print "<!-- start of span $span -->\n";
				
				## lets figure out ourselves what the start and end will be in seconds
				## instead of having rrdtool do it ...
				
				my $end   = time - 300;
				my $start = $end - $span;
				
				my $rrdfile;
				
					foreach my $stat (@stats) {
					
						print "<!-- start of stat $stat -->\n";
						
						@graph_args = @graph_common_args;
					
						if      ($stat eq 'CPU') {
						
							$rrdfile = "$datadir/$host/CPU.rrd";
						
							push (@graph_args, 
								  "--upper-limit",    "100",
								  "--end",            "$end",
								  "--start",          "$start",
								  "--title",          "$host: CPU Usage ($spans_pretty{$span})",
								  "--vertical-label", "% Busy",
								  "--imginfo",
									"<IMG SRC=graphs/%s WIDTH=%lu HEIGHT=%lu ALT=\"$host - $stat - $span\">",
								  "DEF:A=$rrdfile:user_p:AVERAGE",
								  "DEF:B=$rrdfile:system_p:AVERAGE",
								  "CDEF:C=A,B,+",
								  "CDEF:NODATA=A,UN,INF,UNKN,IF",
								  "AREA:NODATA#EFEEED"
							);	  
							
							 
							if ($gsize eq "small") {
							
								push (@graph_args,
									"AREA:A#000066:% User   ",
								    "STACK:B#009900:% System ",
								    "LINE1:C#FFFFFF:Total    "
								);    
								  
							} else {
							
								push (@graph_args,
									"AREA:A#000066:% User   ",
									"GPRINT:A:LAST:\nCur\\: %3.2lf",
									"GPRINT:A:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:A:MIN:Min\\: %3.2lf",
									"GPRINT:A:MAX:Max\\: %3.2lf\\n",
								    "STACK:B#009900:% System ",
									"GPRINT:B:LAST:Cur\\: %3.2lf",
									"GPRINT:B:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:B:MIN:Min\\: %3.2lf",
									"GPRINT:B:MAX:Max\\: %3.2lf\\n",
								    "LINE1:C#FFFFFF:Total    ",
									"GPRINT:C:LAST:Cur\\: %3.2lf",
									"GPRINT:C:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:C:MIN:Min\\: %3.2lf",
									"GPRINT:C:MAX:Max\\: %3.2lf"
								);
								
							};
							
						} elsif ($stat eq 'LOAD') {
						
							$rrdfile = "$datadir/$host/LOAD.rrd";
						
							push (@graph_args,
								  "--upper-limit",    "10",
								  "--end",            "$end",
								  "--start",          "$start",
								  "--title",          "$host: Load Average ($spans_pretty{$span})",
								  "--vertical-label", "Load Average",
								  "--imginfo",
									"<IMG SRC=graphs/%s WIDTH=%lu HEIGHT=%lu ALT=\"$host - $stat - $span\">",
								  "DEF:A=$rrdfile:load_01:AVERAGE",
								  "DEF:B=$rrdfile:load_05:AVERAGE",
								  "DEF:C=$rrdfile:load_15:AVERAGE",
								  "CDEF:NODATA=A,UN,INF,UNKN,IF",
								  "AREA:NODATA#EFEEED",
							);

							if ($gsize eq "small") {
							
								push (@graph_args,
								  "LINE1:A#000066:1 Minute ",
								  "LINE2:B#009900:5 Minute ",
								  "LINE3:C#FF0000:15 Minute"
								);
																
							} else {

								push (@graph_args,
								  "LINE1:A#000066:1 Minute ",
									"GPRINT:A:LAST:\nCur\\: %3.2lf",
									"GPRINT:A:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:A:MIN:Min\\: %3.2lf",
									"GPRINT:A:MAX:Max\\: %3.2lf\\n",
								  "LINE2:B#009900:5 Minute ",
									"GPRINT:B:LAST:Cur\\: %3.2lf",
									"GPRINT:B:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:B:MIN:Min\\: %3.2lf",
									"GPRINT:B:MAX:Max\\: %3.2lf\\n",
								  "LINE3:C#FF0000:15 Minute",
									"GPRINT:C:LAST:Cur\\: %3.2lf",
									"GPRINT:C:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:C:MIN:Min\\: %3.2lf",
									"GPRINT:C:MAX:Max\\: %3.2lf"

								);
							
							};
							
						} elsif ($stat eq 'SWAP') {
						
							$rrdfile = "$datadir/$host/SWAP.rrd";
						
							push (@graph_args,
								  "--upper-limit",    "100",
								  "--end",            "$end",
								  "--start",          "$start",
								  "--title",          "$host: Paging Usage ($spans_pretty{$span})",
								  "--vertical-label", "% Swap Used",
								  "--imginfo",
									"<IMG SRC=graphs/%s WIDTH=%lu HEIGHT=%lu ALT=\"$host - $stat - $span\">",
								  "DEF:A=$rrdfile:swap_p:AVERAGE",
								  "CDEF:NODATA=A,UN,INF,UNKN,IF",
								  "AREA:NODATA#EFEEED",
							);
						
							if ($gsize eq "small") {
							
								push (@graph_args,
								  "AREA:A#000066:% Swap Used"
								);
								
							} else {
							
								push (@graph_args,
								  "AREA:A#000066:% Swap Used",
									"GPRINT:A:LAST:\nCur\\: %3.2lf",
									"GPRINT:A:AVERAGE:Avg\\: %3.2lf",
									"GPRINT:A:MIN:Min\\: %3.2lf",
									"GPRINT:A:MAX:Max\\: %3.2lf"
								);
							};
							
						};
			
			
				my $rrdlast = RRDs::last ($rrdfile);
				
				if ($rrdlast < $start) {
				
					print "<p align='left'><i>No $stat data available for the span requested.</i></p>";
					
				} else {
				
					my $filename = "graphs/$host.$stat.$span.$gsize.png";
					
					my ($imgtag, $xsize, $ysize) = RRDs::graph ($filename, @graph_args);
					
					my $rrderror = RRDs::error;
					
					if ($rrderror) {
					
						print "<p align='left'><i>RRD Error: $rrderror</i></p>\n";
						
					} else {
					
						printf ("<TR><TD COLSPAN='2' BGCOLOR='#FFFFFF' ALIGN='center'>%s<BR></TD></TR>", @$imgtag);
						
					};
				
					print "<!-- end of stat $stat -->\n";	
					
				};
			};
					
			print '</TD></TR><TR><TD COLSPAN="2" BGCOLOR="#EFEEED" ALIGN="center"><!-- def -->';
		
			print "<!-- end of span $span -->\n";		
		};
		
		print "</TD></TR>";
	
		print "<!-- end of host $host -->\n";
		
	};
	
	print "</TABLE>";
	
};  ## END generate_graphs

###############################################################################

sub print_page_bottom {

	print '</TD><TD WIDTH="40" BGCOLOR="#FFFFFF">
	       <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="15" BORDER="0">
	       </TD></TR></TABLE>';
	
	print '</FORM>';
	       
	print '<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
	       <TR VALIGN="top">
	         <TD COLSPAN="4" BGCOLOR="#000000" WIDTH="100%">
		       <IMG SRC="spacer.gif" ALT="" WIDTH="2" HEIGHT="1" BORDER="0">  
	         </TD>
	       </TR>
	       <TR VALIGN="top">
	         <TD>
		       <IMG SRC="spacer.gif" ALT="" WIDTH="160" HEIGHT="1" BORDER="0"> 
		     </TD>
		     <TD VALIGN="bottom" WIDTH="100%">
		       <IMG SRC="spacer.gif" ALT="" WIDTH="428" HEIGHT="1" BORDER="0"> 
		     </TD>
		     <TD ROWSPAN="2" ALIGN="right">
		       <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="1" BORDER="0">  
		     </TD>
		   </TR>
		   </TABLE>';
		   
	print '<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="100%">
		   <TR VALIGN="top">
		     <TD WIDTH="160">
		       <DIV ALIGN="left" CLASS="smaller"><A HREF="#top">top</A></DIV>
		     </TD>
		     <TD VALIGN="middle">
		       <DIV ALIGN="left" CLASS="smaller">';

	print      "Page generated " . scalar localtime() . ".<BR>
                Generation time: " . scalar time() - $^T . " seconds.
             </TD>";
             
    print '  <TD ALIGN="right" VALIGN="bottom">
               <a href="http://people.ee.ethz.ch/~oetiker/webtools/rrdtool/">
                 <img src="rrdtool.gif" width="120" height="34" border="0">
               </a>
             </TD>
             <TD WIDTH="40">
               <IMG SRC="spacer.gif" ALT="" WIDTH="40" HEIGHT="42" BORDER="0">
             </TD>
           </TR>
           </TABLE>';
             	
	print '</BODY></HTML>';
	
	return
	
};	## END print_page_bottom

###############################################################################
