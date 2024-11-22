void draw_res_temp()
{
        double T[11] = { -50, -25, 0, 25, 50, 75, 100, 125, 150, 175, 200 };
        double R[11] = { 8030.6, 9019.2, 10000, 10973, 11940, 12899, 13851, 14795, 15733, 16663, 17586 };

        TCanvas *c1 = new TCanvas();
        c1->cd();
	
	//auto g = new TGraphErrors(11,T,R,0,0);
        auto g = new TGraphErrors(11,R,T,0,0);
        g->SetMarkerStyle(21);
        //g->SetTitle(" ; T, C; R, Om");
        g->SetTitle(" ; R, Om; T, C");
        g->Draw("ALP");

        TF1* fitl = new TF1("fitl","pol1", 8030.6, 17586 );
        g->Fit("fitl","","",8030.6, 17586);

        c1->SaveAs("curveTR.png");
}
